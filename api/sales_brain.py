import json
import os
import re
import time
import uuid

DATA_DIR = os.path.join(os.path.dirname(__file__), "data")
TURN_LOG_FILE = os.path.join(DATA_DIR, "conversation_turns.jsonl")
LEAD_PROFILE_FILE = os.path.join(DATA_DIR, "lead_profiles.json")

CONTACT_PHONE = "+86 13676797588"
CONTACT_EMAIL = "87333310@qq.com"

INTENT_KEYWORDS = {
    "contact": ["联系", "电话", "微信", "邮箱", "地址", "怎么找你们"],
    "pricing": ["价格", "报价", "费用", "多少钱", "预算", "折扣"],
    "timeline": ["多久", "周期", "时间", "加急", "尽快", "本周", "下周"],
    "materials": ["资料", "材料", "清单", "准备什么", "提交什么"],
    "service": ["认证", "申报", "顾问", "许可证", "服务", "办理", "怎么弄", "怎么办", "流程"],
    "complaint": ["投诉", "律师", "纠纷", "风险", "赔偿", "举报"],
}
INTENT_WEIGHT = {
    "pricing": 3,
    "complaint": 3,
    "timeline": 2,
    "materials": 2,
    "service": 2,
    "contact": 1,
}

SERVICE_HINTS = [
    "体系认证",
    "产品认证",
    "政府项目申报",
    "管理顾问服务",
    "生产许可证",
]

URGENCY_KEYWORDS = {
    "high": ["今天", "马上", "尽快", "加急", "本周", "立刻"],
    "medium": ["这周", "下周", "近期", "尽早"],
}

EMAIL_RE = re.compile(r"[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}")
PHONE_RE = re.compile(r"(?:\+?86[-\s]?)?(1[3-9]\d{9})")
NAME_RE = re.compile(r"(?:我叫|我是|联系人[:：]?)([^\s，。,.]{2,16})")
COMPANY_RE = re.compile(r"([^\s，。,.]{2,40}(?:公司|企业|工厂|集团|工作室))")


def ensure_data_dir():
    os.makedirs(DATA_DIR, exist_ok=True)


def ensure_session_id(session_id):
    if isinstance(session_id, str) and session_id.strip():
        return session_id.strip()[:80]
    return f"sess_{int(time.time() * 1000)}_{uuid.uuid4().hex[:8]}"


def detect_intent(text):
    normalized = (text or "").lower()
    scores = {}
    for intent, keywords in INTENT_KEYWORDS.items():
        hit_count = 0
        for keyword in keywords:
            if keyword in normalized:
                hit_count += 1
        if hit_count > 0:
            scores[intent] = hit_count * INTENT_WEIGHT.get(intent, 1)
    if scores:
        return max(scores, key=scores.get)
    return "general"


def detect_service_intent(text):
    text = text or ""
    for item in SERVICE_HINTS:
        if item in text:
            return item
    if "iso" in text.lower():
        return "体系认证"
    return ""


def detect_urgency(text):
    text = text or ""
    for level, keywords in URGENCY_KEYWORDS.items():
        if any(keyword in text for keyword in keywords):
            return level
    return "low"


def extract_lead_fields(text):
    text = text or ""
    lead = {}

    email_match = EMAIL_RE.search(text)
    if email_match:
        lead["email"] = email_match.group(0)

    phone_match = PHONE_RE.search(text)
    if phone_match:
        lead["phone"] = phone_match.group(1)

    name_match = NAME_RE.search(text)
    if name_match:
        lead["contact_name"] = name_match.group(1)

    company_match = COMPANY_RE.search(text)
    if company_match:
        lead["company_name"] = company_match.group(1)

    service_intent = detect_service_intent(text)
    if service_intent:
        lead["service_intent"] = service_intent

    urgency = detect_urgency(text)
    if urgency != "low":
        lead["urgency"] = urgency

    return lead


def calc_lead_score(lead, intent, history):
    score = 0
    if lead.get("phone"):
        score += 35
    if lead.get("contact_name"):
        score += 20
    if lead.get("company_name"):
        score += 20
    if lead.get("service_intent"):
        score += 15
    if lead.get("email"):
        score += 10
    if lead.get("urgency") == "high":
        score += 10

    if intent in ("pricing", "timeline"):
        score += 10

    if isinstance(history, list) and len(history) >= 4:
        score += 5

    return min(score, 100)


def score_to_tier(score):
    if score >= 75:
        return "hot"
    if score >= 40:
        return "warm"
    return "cold"


def choose_next_action(intent, lead, tier):
    required = ["contact_name", "phone", "service_intent"]
    missing = [field for field in required if not lead.get(field)]

    if intent == "complaint":
        return "handoff_support", missing

    if missing:
        return "collect_lead_fields", missing

    if tier == "hot":
        return "schedule_consultation", missing

    if intent in ("pricing", "timeline") and tier in ("warm", "hot"):
        return "schedule_consultation", missing

    return "send_materials_and_followup", missing


def build_sales_guidance(analysis, lead_profile):
    missing_fields = analysis.get("missing_fields", [])
    missing_hint = "、".join(missing_fields) if missing_fields else "无"
    next_action = analysis.get("next_action", "collect_lead_fields")

    if next_action == "collect_lead_fields":
        action_hint = "本轮优先补齐关键字段（联系人、电话、服务意向），一次最多追问1个字段。"
        if analysis.get("intent") == "contact":
            action_hint = "用户在问联系方式，优先引导其留下姓名+电话（或微信）+方便联系时间，由顾问主动联系；电话邮箱作为备选。"
    elif next_action == "schedule_consultation":
        action_hint = "推动预约顾问沟通，给出可执行下一步（电话沟通/提交资料）。"
    elif next_action == "handoff_support":
        action_hint = "立即转人工并给出联系方式，避免继续自动承诺。"
    else:
        action_hint = "提供资料模板并确认后续跟进时间。"

    return f"""
【销售推进状态】
- 意图: {analysis.get("intent", "general")}
- 线索等级: {analysis.get("lead_tier", "cold")}（score={analysis.get("lead_score", 0)}）
- 缺失字段: {missing_hint}
- 当前推荐动作: {next_action}
- 已收集线索: {json.dumps(lead_profile, ensure_ascii=False)}

【销售执行要求】
1. 你的目标是“解疑 + 匹配服务 + 推进成交”，不要停在知识性回答。
2. 回答问题后，必须给出一个明确下一步动作（预约沟通/清单评估/留资跟进）。
3. 若缺失关键信息，优先收集，不要一次提太多问题。
4. 若用户话题出现明显行业切换，先澄清是否同一家公司新业务或另一家企业需求，再继续方案推进。
5. 价格和承诺类问题给出条件范围，不给绝对承诺。
6. 若需要人工，明确引导联系：电话 {CONTACT_PHONE}，邮箱 {CONTACT_EMAIL}。
7. 本轮执行重点：{action_hint}
"""


def _load_lead_profiles():
    if not os.path.exists(LEAD_PROFILE_FILE):
        return {}
    try:
        with open(LEAD_PROFILE_FILE, "r", encoding="utf-8") as f:
            data = json.load(f)
        if isinstance(data, dict):
            return data
    except Exception:
        pass
    return {}


def _save_lead_profiles(data):
    with open(LEAD_PROFILE_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


def merge_lead_profile(session_id, extracted):
    ensure_data_dir()
    all_profiles = _load_lead_profiles()
    current = all_profiles.get(session_id, {})

    for key, value in extracted.items():
        if isinstance(value, str) and value.strip():
            current[key] = value.strip()

    current["updated_at"] = int(time.time())
    all_profiles[session_id] = current
    _save_lead_profiles(all_profiles)
    return current


def analyze_turn(user_message, history, session_id):
    extracted = extract_lead_fields(user_message)
    context_parts = []
    if isinstance(history, list):
        for item in history[-6:]:
            if isinstance(item, dict) and item.get("role") == "user":
                content = item.get("content")
                if isinstance(content, str) and content.strip():
                    context_parts.append(content.strip())
    if user_message:
        context_parts.append(user_message)
    context_text = " ".join(context_parts).strip()

    intent = detect_intent(context_text or user_message)
    if not extracted.get("service_intent"):
        service_intent = detect_service_intent(context_text or user_message)
        if service_intent:
            extracted["service_intent"] = service_intent

    score = calc_lead_score(extracted, intent, history)
    tier = score_to_tier(score)
    next_action, missing_fields = choose_next_action(intent, extracted, tier)

    return {
        "session_id": session_id,
        "intent": intent,
        "lead_score": score,
        "lead_tier": tier,
        "next_action": next_action,
        "missing_fields": missing_fields,
        "extracted_lead": extracted,
    }


def append_turn_log(session_id, user_message, assistant_reply, analysis, model, ok=True, error=""):
    ensure_data_dir()
    record = {
        "ts": int(time.time()),
        "session_id": session_id,
        "ok": ok,
        "error": error,
        "model": model,
        "user_message": user_message,
        "assistant_reply": assistant_reply,
        "analysis": analysis,
    }
    with open(TURN_LOG_FILE, "a", encoding="utf-8") as f:
        f.write(json.dumps(record, ensure_ascii=False) + "\n")
