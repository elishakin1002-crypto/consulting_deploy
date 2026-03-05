from http.server import BaseHTTPRequestHandler
import json
import os
import ssl
import time
import urllib.request
import urllib.error
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

def _normalize_api_key(raw_value):
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


# 配置
API_KEY = _normalize_api_key(os.environ.get("MOONSHOT_API_KEY", ""))
MOONSHOT_API_URL = "https://api.moonshot.cn/v1/chat/completions"
MOONSHOT_MODEL = os.environ.get("MOONSHOT_MODEL", "moonshot-v1-8k").strip()
ALLOW_INSECURE_SSL = os.environ.get("MOONSHOT_INSECURE_SKIP_VERIFY", "0").strip() == "1"
CUSTOM_CA_FILE = (
    os.environ.get("MOONSHOT_CA_BUNDLE")
    or os.environ.get("SSL_CERT_FILE")
    or os.environ.get("REQUESTS_CA_BUNDLE")
    or ""
).strip()

try:
    import certifi  # type: ignore
except Exception:
    certifi = None

# 加载知识库
try:
    knowledge_path = os.path.join(os.path.dirname(__file__), 'knowledge.txt')
    with open(knowledge_path, 'r', encoding='utf-8') as f:
        KNOWLEDGE_BASE = f.read()
except Exception as e:
    KNOWLEDGE_BASE = "暂无详细公司信息，请根据通用商业知识回答。"

class handler(BaseHTTPRequestHandler):
    def do_POST(self):
        send_json = lambda code, payload: handler._send_json(self, code, payload)
        session_id = ""
        user_message = ""
        safe_history = []
        pre_analysis = {}
        lead_profile = {}
        try:
            client_api_key = _normalize_api_key(self.headers.get("X-API-Key"))
            current_api_key = API_KEY or client_api_key

            if not current_api_key:
                send_json(500, {"error": "服务端未配置 MOONSHOT_API_KEY"})
                return

            content_length = int(self.headers.get('Content-Length', '0'))
            if content_length <= 0:
                send_json(400, {"error": "请求体为空"})
                return

            post_data = self.rfile.read(content_length)

            data = json.loads(post_data.decode('utf-8'))
            user_message = (data.get('message', '') or '').strip()
            history = data.get('history', [])
            session_id = ensure_session_id(data.get("session_id") or self.headers.get("X-Session-Id"))

            if not user_message:
                send_json(400, {"error": "message 不能为空"})
                return

            if isinstance(history, list):
                for item in history[-10:]:
                    if not isinstance(item, dict):
                        continue
                    role = item.get("role")
                    content = item.get("content")
                    if role in ("user", "assistant") and isinstance(content, str) and content.strip():
                        safe_history.append({"role": role, "content": content.strip()})

            pre_analysis = analyze_turn(user_message, safe_history, session_id)
            lead_profile = merge_lead_profile(session_id, pre_analysis.get("extracted_lead", {}))
            sales_guidance = build_sales_guidance(pre_analysis, lead_profile)
            policy_prompt = build_policy_prompt(user_message, safe_history)
            
            # 构造系统提示词
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

            # 构造 Moonshot API 请求
            messages = [{"role": "system", "content": system_prompt}]
            messages.extend(safe_history)
            messages.append({"role": "user", "content": user_message})
            
            api_payload = {
                "model": MOONSHOT_MODEL,
                "messages": messages,
                "temperature": 0.2
            }
            
            req = urllib.request.Request(
                MOONSHOT_API_URL,
                data=json.dumps(api_payload).encode('utf-8'),
                headers={
                    "Content-Type": "application/json",
                    "Authorization": f"Bearer {current_api_key}"
                }
            )

            ssl_context = handler._build_ssl_context()
            last_network_error = None
            for attempt in range(3):
                try:
                    with urllib.request.urlopen(req, timeout=15, context=ssl_context) as response:
                        api_response = response.read()
                        provider_data = json.loads(api_response.decode('utf-8'))
                        reply = ""
                        if provider_data.get("choices"):
                            message = provider_data["choices"][0].get("message", {})
                            reply = message.get("content", "")
                        reply = enforce_policy_reply(user_message, safe_history, reply)

                        send_json(200, {
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
                            }
                        })
                        append_turn_log(
                            session_id=session_id,
                            user_message=user_message,
                            assistant_reply=reply,
                            analysis=pre_analysis,
                            model=provider_data.get("model", MOONSHOT_MODEL),
                            ok=True,
                        )
                        return
                except urllib.error.URLError as e:
                    last_network_error = e
                    if attempt < 2:
                        time.sleep(0.4 * (attempt + 1))
                        continue
                    raise

        except urllib.error.HTTPError as e:
            try:
                provider_error = e.read().decode('utf-8')
            except Exception:
                provider_error = ""
            append_turn_log(
                session_id=session_id or "unknown",
                user_message=user_message,
                assistant_reply="",
                analysis=pre_analysis,
                model=MOONSHOT_MODEL,
                ok=False,
                error=f"HTTPError:{e.code}",
            )
            send_json(e.code, {"error": "上游模型服务调用失败", "detail": provider_error[:300]})
        except urllib.error.URLError as e:
            reason = str(getattr(e, "reason", "") or e)
            append_turn_log(
                session_id=session_id or "unknown",
                user_message=user_message,
                assistant_reply="",
                analysis=pre_analysis,
                model=MOONSHOT_MODEL,
                ok=False,
                error=f"URLError:{reason[:160]}",
            )
            if "CERTIFICATE_VERIFY_FAILED" in reason or "certificate verify failed" in reason:
                send_json(502, {
                    "error": "SSL 证书校验失败，请在服务端配置可信 CA（SSL_CERT_FILE / MOONSHOT_CA_BUNDLE），或仅在本地调试时设置 MOONSHOT_INSECURE_SKIP_VERIFY=1"
                })
            else:
                send_json(502, {"error": f"上游网络连接失败: {reason[:160]}"})
        except json.JSONDecodeError:
            send_json(400, {"error": "JSON 格式错误"})
        except Exception:
            append_turn_log(
                session_id=session_id or "unknown",
                user_message=user_message,
                assistant_reply="",
                analysis=pre_analysis,
                model=MOONSHOT_MODEL,
                ok=False,
                error="InternalError",
            )
            send_json(500, {"error": "服务暂时不可用，请稍后重试"})

    def _send_json(self, status_code, payload):
        self.send_response(status_code)
        self.send_header('Content-type', 'application/json; charset=utf-8')
        self.end_headers()
        self.wfile.write(json.dumps(payload, ensure_ascii=False).encode('utf-8'))

    @staticmethod
    def _build_ssl_context():
        if ALLOW_INSECURE_SSL:
            return ssl._create_unverified_context()

        if CUSTOM_CA_FILE:
            return ssl.create_default_context(cafile=CUSTOM_CA_FILE)

        if certifi is not None:
            try:
                return ssl.create_default_context(cafile=certifi.where())
            except Exception:
                pass

        return ssl.create_default_context()
