import json
import os
import time
from typing import Any, Dict, List

import certifi
import requests
from flask import Flask, jsonify, request

try:
    from api.response_policy import build_policy_prompt, enforce_policy_reply
except Exception:
    from response_policy import build_policy_prompt, enforce_policy_reply  # type: ignore

try:
    from api.sales_brain import (
        append_turn_log,
        analyze_turn,
        build_sales_guidance,
        ensure_session_id,
        merge_lead_profile,
    )
except Exception:
    from sales_brain import (  # type: ignore
        append_turn_log,
        analyze_turn,
        build_sales_guidance,
        ensure_session_id,
        merge_lead_profile,
    )


def _normalize_api_key(raw_value: str) -> str:
    key = (raw_value or "").strip()
    if not key:
        return ""
    lowered = key.lower()
    placeholder_values = {
        "<set>",
        "your_api_key_here",
        "replace_me",
        "changeme",
    }
    if lowered in placeholder_values:
        return ""
    if key.startswith("sk-xxxxxxxx") or key.startswith("sk-XXXX"):
        return ""
    return key


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
REQUEST_TIMEOUT_SECONDS = float(os.environ.get("UPSTREAM_TIMEOUT_SECONDS", "15"))


def _safe_append_turn_log(**kwargs: Any) -> None:
    try:
        append_turn_log(**kwargs)
    except Exception:
        # Vercel serverless file system is read-only in most paths.
        pass


def _safe_merge_lead_profile(session_id: str, extracted: Dict[str, Any]) -> Dict[str, Any]:
    try:
        return merge_lead_profile(session_id, extracted)
    except Exception:
        # Keep chat available even if profile persistence fails.
        return extracted if isinstance(extracted, dict) else {}


def _resolve_verify_setting() -> Any:
    if ALLOW_INSECURE_SSL:
        return False
    if CUSTOM_CA_FILE:
        return CUSTOM_CA_FILE
    return certifi.where()


def _load_knowledge_base() -> str:
    try:
        knowledge_path = os.path.join(os.path.dirname(__file__), "knowledge.txt")
        with open(knowledge_path, "r", encoding="utf-8") as f:
            return f.read()
    except Exception:
        return "暂无详细公司信息，请根据通用商业知识回答。"


KNOWLEDGE_BASE = _load_knowledge_base()
app = Flask(__name__)


def _json_response(payload: Dict[str, Any], status_code: int):
    resp = jsonify(payload)
    resp.status_code = status_code
    resp.headers["Access-Control-Allow-Origin"] = "*"
    resp.headers["Access-Control-Allow-Headers"] = "Content-Type, X-API-Key, Authorization"
    resp.headers["Access-Control-Allow-Methods"] = "GET, POST, OPTIONS"
    return resp


def _extract_api_key(payload: Dict[str, Any]) -> str:
    client_api_key = _normalize_api_key(request.headers.get("X-API-Key", ""))
    auth_header = request.headers.get("Authorization", "").strip()
    if auth_header.lower().startswith("bearer "):
        bearer_key = _normalize_api_key(auth_header.split(" ", 1)[1].strip())
        if bearer_key:
            client_api_key = bearer_key
    body_key = _normalize_api_key(
        str(payload.get("api_key") or payload.get("apiKey") or payload.get("key") or "")
    )
    return API_KEY or client_api_key or body_key


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


@app.route("/", methods=["GET", "POST", "OPTIONS"])
@app.route("/api/chat", methods=["GET", "POST", "OPTIONS"])
def chat():
    if request.method == "OPTIONS":
        return _json_response({"ok": True}, 204)

    if request.method == "GET":
        return _json_response({"ok": True, "service": "xinyi-chat-api", "model": MOONSHOT_MODEL}, 200)

    session_id = ""
    user_message = ""
    safe_history: List[Dict[str, str]] = []
    pre_analysis: Dict[str, Any] = {}

    try:
        data = request.get_json(silent=True)
        if data is None:
            return _json_response({"error": "JSON 格式错误"}, 400)

        current_api_key = _extract_api_key(data)
        if not current_api_key:
            return _json_response({"error": "服务端未配置 MOONSHOT_API_KEY"}, 500)

        user_message = (data.get("message", "") or "").strip()
        if not user_message:
            return _json_response({"error": "message 不能为空"}, 400)

        safe_history = _normalize_history(data.get("history", []))
        session_id = ensure_session_id(data.get("session_id") or request.headers.get("X-Session-Id"))

        pre_analysis = analyze_turn(user_message, safe_history, session_id)
        lead_profile = _safe_merge_lead_profile(session_id, pre_analysis.get("extracted_lead", {}))
        sales_guidance = build_sales_guidance(pre_analysis, lead_profile)
        policy_prompt = build_policy_prompt(user_message, safe_history)

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

        payload = {
            "model": MOONSHOT_MODEL,
            "messages": messages,
            "temperature": 0.2,
        }

        resp = requests.post(
            MOONSHOT_API_URL,
            json=payload,
            headers={
                "Content-Type": "application/json",
                "Authorization": f"Bearer {current_api_key}",
            },
            timeout=REQUEST_TIMEOUT_SECONDS,
            verify=_resolve_verify_setting(),
        )

        if resp.status_code >= 400:
            detail = (resp.text or "")[:300]
            _safe_append_turn_log(
                session_id=session_id or "unknown",
                user_message=user_message,
                assistant_reply="",
                analysis=pre_analysis,
                model=MOONSHOT_MODEL,
                ok=False,
                error=f"HTTPError:{resp.status_code}",
            )
            return _json_response({"error": "上游模型服务调用失败", "detail": detail}, resp.status_code)

        provider_data = resp.json()
        reply = ""
        if provider_data.get("choices"):
            message = provider_data["choices"][0].get("message", {})
            reply = message.get("content", "")
        reply = enforce_policy_reply(user_message, safe_history, reply)

        _safe_append_turn_log(
            session_id=session_id,
            user_message=user_message,
            assistant_reply=reply,
            analysis=pre_analysis,
            model=provider_data.get("model", MOONSHOT_MODEL),
            ok=True,
        )

        return _json_response(
            {
                "reply": reply,
                "choices": provider_data.get("choices", []),
                "model": provider_data.get("model", MOONSHOT_MODEL),
                "session_id": session_id,
                "sales": {
                    "intent": pre_analysis.get("intent"),
                    "lead_tier": pre_analysis.get("lead_tier"),
                    "lead_score": pre_analysis.get("lead_score"),
                    "next_action": pre_analysis.get("next_action"),
                    "missing_fields": pre_analysis.get("missing_fields"),
                },
            },
            200,
        )

    except requests.exceptions.SSLError:
        _safe_append_turn_log(
            session_id=session_id or "unknown",
            user_message=user_message,
            assistant_reply="",
            analysis=pre_analysis,
            model=MOONSHOT_MODEL,
            ok=False,
            error="SSLError",
        )
        return _json_response(
            {
                "error": "SSL 证书校验失败，请在服务端配置可信 CA（SSL_CERT_FILE / MOONSHOT_CA_BUNDLE），或仅在本地调试时设置 MOONSHOT_INSECURE_SKIP_VERIFY=1"
            },
            502,
        )
    except requests.exceptions.Timeout:
        _safe_append_turn_log(
            session_id=session_id or "unknown",
            user_message=user_message,
            assistant_reply="",
            analysis=pre_analysis,
            model=MOONSHOT_MODEL,
            ok=False,
            error="Timeout",
        )
        return _json_response({"error": "上游模型服务超时，请稍后重试"}, 504)
    except requests.exceptions.RequestException as e:
        _safe_append_turn_log(
            session_id=session_id or "unknown",
            user_message=user_message,
            assistant_reply="",
            analysis=pre_analysis,
            model=MOONSHOT_MODEL,
            ok=False,
            error=f"RequestException:{str(e)[:120]}",
        )
        return _json_response({"error": f"上游网络连接失败: {str(e)[:160]}"}, 502)
    except Exception:
        _safe_append_turn_log(
            session_id=session_id or "unknown",
            user_message=user_message,
            assistant_reply="",
            analysis=pre_analysis,
            model=MOONSHOT_MODEL,
            ok=False,
            error="InternalError",
        )
        return _json_response({"error": "服务暂时不可用，请稍后重试"}, 500)


# Vercel Python runtime uses this WSGI app entry.
handler = app
