import importlib.util
import json
import os
import ssl
import time
import urllib.error
import urllib.request
from http.server import BaseHTTPRequestHandler
from typing import Any, Dict, List


MODULE_LOAD_ERROR = ""
BUILD_POLICY_PROMPT = None
ENFORCE_POLICY_REPLY = None
APPEND_TURN_LOG = None
ANALYZE_TURN = None
BUILD_SALES_GUIDANCE = None
ENSURE_SESSION_ID = None
MERGE_LEAD_PROFILE = None


def _normalize_api_key(raw_value: str) -> str:
    key = (raw_value or "").strip()
    if not key:
        return ""
    lowered = key.lower()
    placeholder_values = {"<set>", "your_api_key_here", "replace_me", "changeme"}
    if lowered in placeholder_values:
        return ""
    if key.startswith("sk-xxxxxxxx") or key.startswith("sk-XXXX"):
        return ""
    return key


def _safe_timeout_seconds() -> float:
    raw = os.environ.get("UPSTREAM_TIMEOUT_SECONDS", "30")
    try:
        return max(5.0, float(raw))
    except Exception:
        return 30.0


def _safe_retry_attempts() -> int:
    raw = os.environ.get("UPSTREAM_RETRY_ATTEMPTS", "3")
    try:
        return max(1, min(5, int(raw)))
    except Exception:
        return 3


def _safe_retry_backoff_seconds() -> float:
    raw = os.environ.get("UPSTREAM_RETRY_BACKOFF_SECONDS", "0.8")
    try:
        return max(0.2, min(5.0, float(raw)))
    except Exception:
        return 0.8


def _is_retryable_upstream_error(http_code: int, detail: str) -> bool:
    normalized = (detail or "").lower()
    if http_code in (429, 500, 502, 503, 504):
        return True
    return any(
        token in normalized
        for token in (
            "engine_overloaded_error",
            "overloaded",
            "rate limit",
            "temporarily unavailable",
            "try again later",
            "service unavailable",
        )
    )


def _build_retry_delay(attempt_index: int) -> float:
    base = _safe_retry_backoff_seconds()
    return base * float(attempt_index + 1)


def _load_module_from_file(module_name: str):
    current_dir = os.path.dirname(__file__)
    file_path = os.path.join(current_dir, f"{module_name}.py")
    if not os.path.exists(file_path):
        raise FileNotFoundError(file_path)
    spec = importlib.util.spec_from_file_location(module_name, file_path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot load spec for {module_name}")
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def _boot_modules() -> None:
    global MODULE_LOAD_ERROR
    global BUILD_POLICY_PROMPT, ENFORCE_POLICY_REPLY
    global APPEND_TURN_LOG, ANALYZE_TURN, BUILD_SALES_GUIDANCE, ENSURE_SESSION_ID, MERGE_LEAD_PROFILE

    try:
        policy_mod = _load_module_from_file("response_policy")
        sales_mod = _load_module_from_file("sales_brain")

        BUILD_POLICY_PROMPT = getattr(policy_mod, "build_policy_prompt")
        ENFORCE_POLICY_REPLY = getattr(policy_mod, "enforce_policy_reply")

        APPEND_TURN_LOG = getattr(sales_mod, "append_turn_log")
        ANALYZE_TURN = getattr(sales_mod, "analyze_turn")
        BUILD_SALES_GUIDANCE = getattr(sales_mod, "build_sales_guidance")
        ENSURE_SESSION_ID = getattr(sales_mod, "ensure_session_id")
        MERGE_LEAD_PROFILE = getattr(sales_mod, "merge_lead_profile")
    except Exception as e:
        MODULE_LOAD_ERROR = f"{type(e).__name__}: {str(e)[:240]}"


API_KEY = _normalize_api_key(
    os.environ.get("KIMI_API_KEY")
    or os.environ.get("MOONSHOT_API_KEY")
    or os.environ.get("API_KEY", "")
)
MOONSHOT_API_URL = os.environ.get("KIMI_BASE_URL", "https://api.moonshot.cn/v1").rstrip("/") + "/chat/completions"
MOONSHOT_MODEL = (os.environ.get("KIMI_MODEL") or os.environ.get("MOONSHOT_MODEL") or "kimi-k2.5").strip()
ALLOW_INSECURE_SSL = os.environ.get("MOONSHOT_INSECURE_SKIP_VERIFY", "0").strip() == "1"
CUSTOM_CA_FILE = (
    os.environ.get("MOONSHOT_CA_BUNDLE")
    or os.environ.get("SSL_CERT_FILE")
    or os.environ.get("REQUESTS_CA_BUNDLE")
    or ""
).strip()
REQUEST_TIMEOUT_SECONDS = _safe_timeout_seconds()
UPSTREAM_RETRY_ATTEMPTS = _safe_retry_attempts()


_boot_modules()


def _load_knowledge_base() -> str:
    try:
        knowledge_path = os.path.join(os.path.dirname(__file__), "knowledge.txt")
        with open(knowledge_path, "r", encoding="utf-8") as f:
            return f.read()
    except Exception:
        return "暂无详细公司信息，请根据通用商业知识回答。"


KNOWLEDGE_BASE = _load_knowledge_base()


def _resolve_ssl_context() -> ssl.SSLContext:
    if ALLOW_INSECURE_SSL:
        return ssl._create_unverified_context()
    if CUSTOM_CA_FILE:
        return ssl.create_default_context(cafile=CUSTOM_CA_FILE)
    return ssl.create_default_context()


def _safe_append_turn_log(**kwargs: Any) -> None:
    if APPEND_TURN_LOG is None:
        return
    try:
        APPEND_TURN_LOG(**kwargs)
    except Exception:
        pass


def _safe_merge_lead_profile(session_id: str, extracted: Dict[str, Any]) -> Dict[str, Any]:
    if MERGE_LEAD_PROFILE is None:
        return extracted if isinstance(extracted, dict) else {}
    try:
        return MERGE_LEAD_PROFILE(session_id, extracted)
    except Exception:
        return extracted if isinstance(extracted, dict) else {}


def _normalize_history(raw_history: Any) -> List[Dict[str, str]]:
    safe_history: List[Dict[str, str]] = []
    if not isinstance(raw_history, list):
        return safe_history
    for item in raw_history[-10:]:
        if not isinstance(item, dict):
            continue
        role = item.get("role")
        content = item.get("content")
        if role in ("user", "assistant") and isinstance(content, str) and content.strip():
            safe_history.append({"role": role, "content": content.strip()})
    return safe_history


class handler(BaseHTTPRequestHandler):
    def _send_json(self, status_code: int, payload: Dict[str, Any]) -> None:
        body = json.dumps(payload, ensure_ascii=False).encode("utf-8")
        self.send_response(status_code)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Headers", "Content-Type")
        self.send_header("Access-Control-Allow-Methods", "GET, POST, OPTIONS")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def do_OPTIONS(self):
        self._send_json(204, {"ok": True})

    def do_GET(self):
        self._send_json(200, {"ok": True, "service": "xinyi-chat-api", "status": "online"})

    def do_POST(self):
        if MODULE_LOAD_ERROR:
            self._send_json(500, {"error": "服务端模块加载失败", "detail": MODULE_LOAD_ERROR})
            return

        if not all([
            BUILD_POLICY_PROMPT,
            ENFORCE_POLICY_REPLY,
            ANALYZE_TURN,
            BUILD_SALES_GUIDANCE,
            ENSURE_SESSION_ID,
        ]):
            self._send_json(500, {"error": "服务端模块未就绪"})
            return

        try:
            content_length = int(self.headers.get("Content-Length", "0") or "0")
            raw = self.rfile.read(content_length) if content_length > 0 else b"{}"
            try:
                data = json.loads(raw.decode("utf-8")) if raw else {}
            except Exception:
                self._send_json(400, {"error": "JSON 格式错误"})
                return

            if not API_KEY:
                self._send_json(500, {"error": "服务端未配置 AI 服务密钥"})
                return

            user_message = (data.get("message", "") or "").strip()
            if not user_message:
                self._send_json(400, {"error": "message 不能为空"})
                return

            safe_history = _normalize_history(data.get("history", []))
            session_id = ENSURE_SESSION_ID(data.get("session_id") or self.headers.get("X-Session-Id"))

            pre_analysis = ANALYZE_TURN(user_message, safe_history, session_id)
            lead_profile = _safe_merge_lead_profile(session_id, pre_analysis.get("extracted_lead", {}))
            sales_guidance = BUILD_SALES_GUIDANCE(pre_analysis, lead_profile)
            policy_prompt = BUILD_POLICY_PROMPT(user_message, safe_history)

            system_prompt = f"""
你是浙江信义企业管理有限公司的智能顾问，名字叫'信义智能助手'。
请基于以下【公司知识库】内容，专业、热情地回答客户问题。

【公司知识库】
{KNOWLEDGE_BASE}

【回答原则】
1. 优先使用知识库中的信息回答。
2. 如果知识库中没有答案，请礼貌地引导客户联系人工客服（电话：+86 13676797588，邮箱：87333310@qq.com）。
3. 回答要简洁明了，语气商务且亲切。
4. 不要编造虚假信息。
5. 每轮对话都应有“下一步行动建议”，推动客户进入咨询或留资。
6. 在官网咨询场景下，涉及“办厂/生产/开店/开公司”等问题时，优先从“合规准入（许可/认证）路径”回答，不先展开泛市场经营建议。
7. 默认身份是“信义咨询顾问”，先回答本公司可承接的认证/许可/企业管理咨询路径；只有用户明确要求时，再展开非核心经营建议。
8. 对“具体怎么弄/怎么办”等追问，必须承接上一轮结论，不得重新从市场调研起盘。
9. 不要机械按字面关键词回答，要结合咨询场景、上下文和用户最终目的做推理。
10. 若用户行业/企业身份疑似切换，先澄清“同一公司新业务还是另一家企业”，再给方案。
"""
            system_prompt = f"{system_prompt}\n{sales_guidance}"
            if policy_prompt:
                system_prompt = f"{system_prompt}\n{policy_prompt}"

            messages: List[Dict[str, str]] = [{"role": "system", "content": system_prompt}]
            messages.extend(safe_history)
            messages.append({"role": "user", "content": user_message})

            provider_data: Dict[str, Any] = {}
            last_error_code = 0
            last_error_detail = ""
            for attempt_index in range(UPSTREAM_RETRY_ATTEMPTS):
                payload = {
                    "model": MOONSHOT_MODEL,
                    "messages": messages,
                }
                req = urllib.request.Request(
                    MOONSHOT_API_URL,
                    data=json.dumps(payload, ensure_ascii=False).encode("utf-8"),
                    headers={
                        "Content-Type": "application/json",
                        "Authorization": f"Bearer {API_KEY}",
                    },
                    method="POST",
                )

                try:
                    with urllib.request.urlopen(
                        req,
                        timeout=REQUEST_TIMEOUT_SECONDS,
                        context=_resolve_ssl_context(),
                    ) as resp:
                        resp_body = resp.read().decode("utf-8", errors="ignore")
                        provider_data = json.loads(resp_body)
                        last_error_code = 0
                        last_error_detail = ""
                        break
                except urllib.error.HTTPError as e:
                    try:
                        detail = (e.read().decode("utf-8", errors="ignore") or "")[:300]
                    except Exception:
                        detail = str(e)[:300]
                    last_error_code = int(e.code or 502)
                    last_error_detail = detail
                    if _is_retryable_upstream_error(last_error_code, detail) and attempt_index < UPSTREAM_RETRY_ATTEMPTS - 1:
                        time.sleep(_build_retry_delay(attempt_index))
                        continue
                    break
                except urllib.error.URLError as e:
                    last_error_code = 502
                    last_error_detail = str(e.reason)[:160]
                    if attempt_index < UPSTREAM_RETRY_ATTEMPTS - 1:
                        time.sleep(_build_retry_delay(attempt_index))
                        continue
                    break
                except TimeoutError:
                    last_error_code = 504
                    last_error_detail = "timeout"
                    if attempt_index < UPSTREAM_RETRY_ATTEMPTS - 1:
                        time.sleep(_build_retry_delay(attempt_index))
                        continue
                    break

            if not provider_data:
                error_tag = "UpstreamError"
                if last_error_code:
                    error_tag = f"HTTPError:{last_error_code}"
                _safe_append_turn_log(
                    session_id=session_id or "unknown",
                    user_message=user_message,
                    assistant_reply="",
                    analysis=pre_analysis,
                    model=MOONSHOT_MODEL,
                    ok=False,
                    error=error_tag,
                )
                if _is_retryable_upstream_error(last_error_code, last_error_detail):
                    self._send_json(
                        503,
                        {
                            "error": f"上游模型繁忙，已自动重试 {UPSTREAM_RETRY_ATTEMPTS} 次，请稍后再试",
                            "detail": last_error_detail,
                        },
                    )
                    return
                if last_error_code == 504:
                    self._send_json(504, {"error": "上游模型服务超时，请稍后重试"})
                    return
                if last_error_code == 502:
                    self._send_json(502, {"error": f"上游网络连接失败: {last_error_detail}"})
                    return
                self._send_json(last_error_code or 502, {"error": "上游模型服务调用失败", "detail": last_error_detail})
                return

            reply = ""
            if isinstance(provider_data, dict) and provider_data.get("choices"):
                message = provider_data["choices"][0].get("message", {})
                reply = message.get("content", "") if isinstance(message, dict) else ""
            reply = ENFORCE_POLICY_REPLY(user_message, safe_history, reply)

            _safe_append_turn_log(
                session_id=session_id,
                user_message=user_message,
                assistant_reply=reply,
                analysis=pre_analysis,
                model=provider_data.get("model", MOONSHOT_MODEL) if isinstance(provider_data, dict) else MOONSHOT_MODEL,
                ok=True,
            )

            self._send_json(
                200,
                {
                    "reply": reply,
                    "session_id": session_id,
                    "sales": {
                        "intent": pre_analysis.get("intent"),
                        "lead_tier": pre_analysis.get("lead_tier"),
                        "lead_score": pre_analysis.get("lead_score"),
                        "next_action": pre_analysis.get("next_action"),
                        "missing_fields": pre_analysis.get("missing_fields"),
                        "lead_profile": lead_profile,
                    },
                },
            )
        except Exception:
            self._send_json(500, {"error": "服务暂时不可用，请稍后重试"})
