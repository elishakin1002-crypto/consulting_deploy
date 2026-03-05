import re


FOOD_FACTORY_KEYWORDS = [
    "茶饮料",
    "饮料",
    "食品",
    "卤味",
    "熟食",
    "肉制品",
    "预制菜",
    "生产厂",
    "食品厂",
    "食品加工厂",
    "办厂",
    "工厂",
    "生产线",
    "月饼",
    "糕点",
    "烘焙",
    "饼干",
    "食品加工",
    "开厂",
    "开店",
    "开公司",
]

OTHER_PRODUCTION_KEYWORDS = [
    "医疗器械",
    "特种设备",
    "保健食品",
    "化妆品",
    "消毒产品",
    "排水",
    "排污",
    "污水",
    "废水",
    "制造",
    "经营许可证",
    "生产许可证",
]

PRODUCTION_SCENARIO_KEYWORDS = FOOD_FACTORY_KEYWORDS + OTHER_PRODUCTION_KEYWORDS

TON_BAG_EXPORT_KEYWORDS = [
    "吨袋",
    "集装袋",
    "编织袋",
    "fibc",
    "吨包",
]

EXPORT_SCENARIO_KEYWORDS = [
    "出海",
    "出口",
    "外贸",
    "海外",
    "国外",
    "欧美",
    "东南亚",
]

FOOD_REPLY_HINTS = [
    "食品生产许可",
    "sc",
    "qs",
    "卤味",
    "熟食",
    "haccp",
    "iso22000",
    "食品",
]

SC_CONTEXT_KEYWORDS = [
    "sc",
    "食品生产许可",
    "食品生产许可证",
    "许可证",
    "卤味",
    "熟食",
    "食品",
]

CONDITION_QUESTION_KEYWORDS = [
    "具备哪些条件",
    "需要具备哪些条件",
    "需要什么条件",
    "什么条件",
    "哪些条件",
    "哪些要求",
    "有什么要求",
    "办理条件",
    "许可证条件",
    "sc条件",
    "硬件",
    "软件",
    "场地要求",
    "人员要求",
    "制度要求",
]

SC_CONDITION_REPLY_HINTS = [
    "场地",
    "车间",
    "分区",
    "设备",
    "人员",
    "健康证",
    "制度",
    "记录",
    "检验",
    "留样",
    "追溯",
    "召回",
    "清洗消毒",
]

IDENTITY_SWITCH_HINTS = [
    "另外一家",
    "另一家",
    "另一个企业",
    "另一个公司",
    "第二家公司",
    "我们还有",
]

CLARIFY_REPLY_HINTS = [
    "另一家企业",
    "另外一家企业",
    "我先确认",
    "想先确认",
    "是否是",
]

PERMIT_KEYWORDS = [
    "许可证",
    "生产许可证",
    "经营许可证",
    "食品生产许可",
    "sc",
    "qs",
    "要办证",
    "需要办证",
    "认证",
    "怎么弄",
    "怎么弄好",
    "怎么办",
    "流程",
    "资质",
    "需要什么",
]

CERT_SERVICE_CONTEXT_KEYWORDS = [
    "你们",
    "你这里",
    "咨询",
    "办理",
    "认证",
    "许可",
]

AMBIGUOUS_PROCESS_KEYWORDS = [
    "具体怎么弄",
    "怎么弄",
    "怎么做",
    "怎么办",
    "流程怎么走",
    "具体流程",
]

DIY_RECIPE_HINTS = [
    "家庭",
    "自己做",
    "自制",
    "食谱",
    "配方",
    "烤箱",
]

RECIPE_ANSWER_HINTS = [
    "准备原料",
    "制作饼皮",
    "准备馅料",
    "包制",
    "成型",
    "烘烤",
    "食谱",
    "配方",
    "模具",
]

GENERIC_BUSINESS_HINTS = [
    "市场调研",
    "竞争对手",
    "产品开发",
    "包装设计",
    "供应链",
    "营销",
    "销售渠道",
    "品牌",
]

FOLLOWUP_QUERY_KEYWORDS = [
    "具体怎么弄",
    "怎么弄",
    "怎么办",
    "怎么做",
    "具体流程",
    "下一步",
    "然后呢",
    "接下来",
    "需要哪些条件",
    "具备哪些条件",
    "要准备什么",
]

CONSULTING_ANCHOR_HINTS = [
    "许可",
    "许可证",
    "认证",
    "合规",
    "办理",
    "流程",
    "条件",
    "资料",
    "清单",
    "申报",
    "备案",
    "标准",
    "检测",
    "体系",
    "对接",
    "接口",
]

CONTACT_QUERY_KEYWORDS = [
    "如何联系",
    "怎么联系",
    "联系方式",
    "联系你们",
    "联系你",
    "怎么找你们",
    "电话多少",
    "邮箱多少",
    "微信",
]

CONTACT_LEAD_CAPTURE_HINTS = [
    "留下",
    "回电",
    "回访",
    "主动联系",
    "方便联系",
    "方便联系时间",
    "我们联系您",
    "顾问联系您",
]

IDENTITY_LABEL_STOP_WORDS = {
    "这个",
    "那个",
    "这个项目",
    "那个项目",
    "这个业务",
    "那个业务",
    "这种",
    "这个问题",
}

DOMAIN_DISPLAY = {
    "food": "食品/餐饮生产",
    "ton_bag": "吨袋/集装袋",
    "medical_device": "医疗器械",
    "cosmetics": "化妆品",
    "special_equipment": "特种设备",
}

PERMIT_TRACKS = [
    {
        "key": "qs",
        "label": "QS 食品相关产品生产许可",
        "keywords": ["qs", "食品相关产品", "食品生产", "食品加工"],
        "note": "食品相关产品场景常见（历史称谓）；实际执行口径以当地最新监管要求为准。",
    },
    {
        "key": "sc",
        "label": "SC 食品生产许可",
        "keywords": ["食品", "饮料", "卤味", "熟食", "月饼", "糕点", "烘焙", "肉制品", "预制菜", "sc"],
        "note": "食品生产场景核心准入前置，通常应先于经营推广和体系优化。",
    },
    {
        "key": "medical_device",
        "label": "医疗器械经营、生产许可证",
        "keywords": ["医疗器械", "器械", "医械", "二类", "三类"],
        "note": "医疗器械生产或经营场景的法定许可，按经营模式和分类确定办理项。",
    },
    {
        "key": "special_equipment",
        "label": "特种设备设计、制造、安装许可证",
        "keywords": ["特种设备", "锅炉", "压力容器", "电梯", "起重", "安装许可证"],
        "note": "涉及特种设备的设计/制造/安装需按法规取得对应许可。",
    },
    {
        "key": "health_food",
        "label": "保健食品许可证",
        "keywords": ["保健食品", "蓝帽子", "保健品"],
        "note": "保健食品业务需走对应许可/注册备案路径，属强监管领域。",
    },
    {
        "key": "cosmetics",
        "label": "化妆品许可证",
        "keywords": ["化妆品", "护肤品", "彩妆", "洗护"],
        "note": "化妆品生产经营需满足对应许可和备案要求。",
    },
    {
        "key": "disinfection",
        "label": "消毒产品卫生许可证",
        "keywords": ["消毒产品", "消毒液", "消杀", "卫生许可证"],
        "note": "消毒产品场景需满足卫生许可等前置要求。",
    },
    {
        "key": "discharge",
        "label": "排水、排污许可证",
        "keywords": ["排水", "排污", "污水", "废水", "排放"],
        "note": "涉及排放活动需满足环保与排放许可要求。",
    },
]

PERMIT_TRACK_BY_KEY = {track["key"]: track for track in PERMIT_TRACKS}

PERMIT_RESPONSE_HINTS = [
    "许可证",
    "许可",
    "sc",
    "qs",
    "医疗器械",
    "特种设备",
    "保健食品",
    "化妆品",
    "消毒产品",
    "排污",
    "排水",
]


def _contains_any(text, keywords):
    return any(k in text for k in keywords)


def _normalize(text):
    text = (text or "").strip().lower()
    text = re.sub(r"\s+", "", text)
    return text


def _collect_user_text(history, user_message):
    parts = []
    if isinstance(history, list):
        for item in history:
            if isinstance(item, dict) and item.get("role") == "user":
                content = item.get("content")
                if isinstance(content, str) and content.strip():
                    parts.append(content.strip())
    if user_message:
        parts.append(user_message.strip())
    return " ".join(parts)


def _detect_domain(text):
    t = _normalize(text)
    if not t:
        return ""
    if _contains_any(t, TON_BAG_EXPORT_KEYWORDS):
        return "ton_bag"
    if _contains_any(t, ["医疗器械", "医械", "器械"]):
        return "medical_device"
    if _contains_any(t, ["化妆品", "护肤品", "彩妆", "洗护"]):
        return "cosmetics"
    if _contains_any(t, ["特种设备", "锅炉", "压力容器", "电梯", "起重"]):
        return "special_equipment"
    if _contains_any(t, FOOD_FACTORY_KEYWORDS):
        return "food"
    return ""


def _get_previous_user_domain(history):
    if not isinstance(history, list):
        return ""
    for item in reversed(history):
        if isinstance(item, dict) and item.get("role") == "user":
            content = item.get("content")
            if isinstance(content, str) and content.strip():
                domain = _detect_domain(content)
                if domain:
                    return domain
    return ""


def _get_latest_user_message(history):
    if not isinstance(history, list):
        return ""
    for item in reversed(history):
        if isinstance(item, dict) and item.get("role") == "user":
            content = item.get("content")
            if isinstance(content, str) and content.strip():
                return content.strip()
    return ""


def _extract_identity_label(text):
    source = (text or "").strip()
    if not source:
        return ""
    patterns = [
        r"(?:我是|我们是|我做|我们做|我们主营|主营|公司做)([^，。,.；;：:]{1,16})",
        r"(?:做)([^，。,.；;：:]{1,16})(?:的?(?:企业|公司|工厂|生意|业务))",
    ]
    for pattern in patterns:
        matched = re.search(pattern, source)
        if not matched:
            continue
        label = matched.group(1).strip()
        label = re.sub(r"(企业|公司|工厂|生意|业务|项目)$", "", label).strip()
        if not label or label in IDENTITY_LABEL_STOP_WORDS:
            continue
        if len(label) > 12:
            label = label[:12]
        return label
    return ""


def _get_previous_identity_label(history):
    if not isinstance(history, list):
        return ""
    for item in reversed(history):
        if isinstance(item, dict) and item.get("role") == "user":
            content = item.get("content")
            if isinstance(content, str) and content.strip():
                label = _extract_identity_label(content)
                if label:
                    return label
    return ""


def _is_identity_label_changed(previous_label, current_label):
    prev = _normalize(previous_label)
    curr = _normalize(current_label)
    if not prev or not curr:
        return False
    if prev == curr:
        return False
    if prev in curr or curr in prev:
        return False
    return True


def _topic_marker(domain, identity_label):
    if identity_label:
        return identity_label
    if domain:
        return DOMAIN_DISPLAY.get(domain, domain)
    return "当前业务"


def _detect_identity_switch(user_message, history):
    normalized_user = _normalize(user_message)
    if _contains_any(normalized_user, IDENTITY_SWITCH_HINTS):
        return False, "", ""

    previous_domain = _get_previous_user_domain(history)
    current_domain = _detect_domain(user_message)
    previous_label = _get_previous_identity_label(history)
    current_label = _extract_identity_label(user_message)

    domain_switched = (
        bool(previous_domain)
        and bool(current_domain)
        and previous_domain != current_domain
    )
    label_switched = _is_identity_label_changed(previous_label, current_label)

    if not domain_switched and not label_switched:
        return False, "", ""

    previous_marker = _topic_marker(previous_domain, previous_label)
    current_marker = _topic_marker(current_domain, current_label)
    return True, previous_marker, current_marker


def _is_followup_question(user_message, history):
    normalized_user = _normalize(user_message)
    if not normalized_user or not isinstance(history, list) or not history:
        return False
    if _contains_any(normalized_user, FOLLOWUP_QUERY_KEYWORDS):
        return True
    if len(normalized_user) <= 8 and _contains_any(normalized_user, ["然后", "继续", "具体", "下一步"]):
        return True
    return False


def _count_hits(text, keywords):
    count = 0
    for keyword in keywords:
        if keyword in text:
            count += 1
    return count


def _looks_like_generic_restart(reply):
    normalized_reply = _normalize(reply)
    generic_hits = _count_hits(normalized_reply, GENERIC_BUSINESS_HINTS)
    anchor_hits = _count_hits(normalized_reply, CONSULTING_ANCHOR_HINTS)
    first_generic_pos = _find_first_hit_pos(normalized_reply, GENERIC_BUSINESS_HINTS)
    first_anchor_pos = _find_first_hit_pos(normalized_reply, CONSULTING_ANCHOR_HINTS)
    if generic_hits >= 2 and anchor_hits == 0:
        return True
    if generic_hits >= 1 and first_generic_pos >= 0 and (first_anchor_pos < 0 or first_generic_pos < first_anchor_pos):
        return True
    return False


def _build_followup_alignment_fix_reply(user_message, history):
    last_user = _get_latest_user_message(history)
    topic_hint = ""
    if last_user:
        topic_hint = last_user if len(last_user) <= 24 else f"{last_user[:24]}..."
    if topic_hint:
        lead_line = f"我按您上一条“{topic_hint}”继续回答，不重新开新话题。"
    else:
        lead_line = "我按您上一条继续回答，不重新开新话题。"

    user_tail = (user_message or "").strip()
    if user_tail:
        lead_line = f"{lead_line} 您这句“{user_tail}”我理解为要落地步骤。"

    return (
        f"{lead_line}\n"
        "通用推进顺序是：1) 先明确目标事项与适用合规路径；2) 做条件差距评估（场地/人员/制度/资料）；"
        "3) 准备材料并提交办理或实施；4) 按反馈整改并进入下一步执行。\n"
        "为了给您精确版本，我先确认1项：您这步是要推进“办证/认证”、还是“出海合规/系统对接”？"
    )


def _build_general_reasoning_prompt(user_message, history):
    followup_line = (
        "- 本轮属于追问，必须承接上一轮结论，禁止重启到泛市场建议。"
        if _is_followup_question(user_message, history)
        else "- 若后续出现追问（如“具体怎么弄/怎么办”），必须默认承接上一轮结论。"
    )
    return "\n".join(
        [
            "【全局推理主线（任何行业通用）】",
            "- 先判断用户真正意图：准入/条件/流程/资料/报价/周期/出海/系统对接/协同落地。",
            followup_line,
            "- 若检测到用户业务身份或行业切换，先用1句澄清“同一公司新业务还是另一家企业”，再回答当前话题。",
            "- 默认角色是咨询顾问：先回答与本公司服务相关的落地路径，再补充经营建议。",
            "- 回答顺序统一为：结论 -> 原因 -> 最小可执行步骤 -> 下一步推进动作（一次追问1项关键字段）。",
            "- 除非用户明确要求，不输出与咨询场景无关的DIY教程或泛创业清单。",
        ]
    )


def _is_contact_query(user_message):
    normalized_user = _normalize(user_message)
    if not normalized_user:
        return False
    return _contains_any(normalized_user, CONTACT_QUERY_KEYWORDS)


def _build_contact_capture_prompt():
    return """
【联系方式类问题（必须）】
- 用户问“如何联系/联系方式”时，优先引导用户留资，采用“我们主动联系您”的推进方式。
- 回答顺序：先请用户留下姓名+电话（或微信）+方便联系时间，再提供公司电话/邮箱作为备选。
- 不要只给被动联系方式后结束对话。
""".strip()


def _build_contact_capture_fix_reply():
    return (
        "可以的，您可以先留下【姓名 + 电话（或微信）+ 方便联系时间】，我们顾问会主动联系您，"
        "按您的情况一对一给方案和办理顺序。\n"
        "如果您更方便主动联系，也可以直接电话：+86 13676797588，邮箱：87333310@qq.com。"
    )


def _build_identity_switch_prompt(previous_marker, current_marker):
    return "\n".join(
        [
            "【身份切换澄清（必须）】",
            f"- 检测到用户从“{previous_marker}”切到“{current_marker}”话题。",
            "- 第一段先反问澄清：这是同一家公司新业务，还是您另一家企业的需求？",
            "- 澄清后立即按用户当前话题回答，不得沿用上一话题模板。",
            "- 回答要保持销售推进：先解疑，再给下一步推进动作（预约/清单/资料）。",
        ]
    )


def _build_identity_switch_fix_reply(user_message):
    t = _normalize(user_message)
    if _contains_any(t, TON_BAG_EXPORT_KEYWORDS) and _contains_any(t, EXPORT_SCENARIO_KEYWORDS):
        return (
            "我先确认一下：这是您另一家企业（吨袋/集装袋业务）的出海需求吗？\n"
            "如果是，我就按吨袋出海路径给您推进：先确定目标国家、用途和是否涉及危险品，再给对应检测/合规文件与出口单证清单。\n"
            "如果不是，请告诉我是同一家公司拓展新业务，我会按一个项目给您做并行落地顺序。"
        )
    return (
        "我先确认一下：您这轮问题是同一家公司的新业务，还是另一家企业的需求？\n"
        "您确认后我会按当前业务给您一版可执行清单，并给出下一步推进动作。"
    )


def _domain_reply_hints(domain):
    if domain == "food":
        return FOOD_REPLY_HINTS
    if domain == "ton_bag":
        return TON_BAG_EXPORT_KEYWORDS + EXPORT_SCENARIO_KEYWORDS
    if domain == "medical_device":
        return ["医疗器械", "医械", "二类", "三类"]
    if domain == "cosmetics":
        return ["化妆品", "护肤品", "彩妆", "洗护"]
    if domain == "special_equipment":
        return ["特种设备", "锅炉", "压力容器", "电梯", "起重"]
    return []


def _detect_permit_tracks(all_user_text):
    matched = []
    for track in PERMIT_TRACKS:
        if _contains_any(all_user_text, track["keywords"]):
            matched.append(track)

    if matched:
        return matched

    # 默认兜底：生产类咨询至少先锁定生产许可路径
    if _contains_any(all_user_text, FOOD_FACTORY_KEYWORDS):
        return [PERMIT_TRACK_BY_KEY["sc"], PERMIT_TRACK_BY_KEY["qs"]]
    if _contains_any(all_user_text, ["生产", "制造", "办厂", "工厂", "开厂", "生产线"]):
        return PERMIT_TRACKS
    return []


def _format_permit_catalog(tracks):
    if not tracks:
        tracks = PERMIT_TRACKS
    lines = []
    for index, track in enumerate(tracks, start=1):
        lines.append(f"{index}) {track['label']}：{track['note']}")
    return "\n".join(lines)


def _find_first_hit_pos(text, keywords):
    first = -1
    for keyword in keywords:
        pos = text.find(keyword)
        if pos >= 0 and (first < 0 or pos < first):
            first = pos
    return first


def _build_permit_first_fix_reply(user_message, history):
    all_user_text = _normalize(_collect_user_text(history, user_message))
    tracks = _detect_permit_tracks(all_user_text)
    permit_catalog = _format_permit_catalog(tracks)
    track_keys = {track["key"] for track in tracks}
    is_mooncake_like = _contains_any(all_user_text, ["月饼", "糕点", "烘焙"])
    is_luwei_like = _contains_any(all_user_text, ["卤味", "熟食", "肉制品"])
    mentions_export = _contains_any(all_user_text, ["出口", "欧盟", "海外", "外贸"])

    if "medical_device" in track_keys:
        service_line = "按“医疗器械生产/经营”场景，先走医疗器械许可路径。"
    elif "special_equipment" in track_keys:
        service_line = "按“特种设备”场景，先走特种设备许可路径。"
    elif "cosmetics" in track_keys:
        service_line = "按“化妆品生产/经营”场景，先走化妆品许可路径。"
    elif "disinfection" in track_keys:
        service_line = "按“消毒产品”场景，先走卫生许可路径。"
    elif "discharge" in track_keys:
        service_line = "按“排放管理”场景，先走排水/排污许可路径。"
    elif is_mooncake_like:
        service_line = "按“月饼国内生产销售”场景，先走食品生产许可（SC）路径。"
    elif is_luwei_like:
        service_line = "按“卤味/熟食国内生产销售”场景，先走食品生产许可（SC）路径。"
    else:
        service_line = "按“生产/办厂”场景，先锁定对应生产许可路径。"

    export_line = (
        "若您明确要出口，再按目标国家补充出口合规和对应认证。"
        if mentions_export
        else "您未提到出口，当前不建议先做海外认证清单。"
    )

    if "sc" in track_keys or "qs" in track_keys:
        suggestion_line = "1) ISO22000 / HACCP：用于提升食品安全管理能力与客户信任，通常不是开工前的硬前置。"
        not_priority_line = f"1) CCC 不作为食品生产默认前置。2) {export_line}"
    elif "medical_device" in track_keys:
        suggestion_line = "1) 管理体系和质量体系可在许可路径明确后规划（按业务需要选择实施）。"
        not_priority_line = f"1) 未提出口时，不先展开海外认证清单。2) {export_line}"
    else:
        suggestion_line = "1) 管理体系与管理咨询可在许可路径明确后并行规划（流程、成本、效率）。"
        not_priority_line = f"1) 非当前业务场景的许可不作为默认前置。2) {export_line}"

    return (
        "您这个问题在信义咨询场景下，默认先走“生产许可/准入”路径。\n"
        f"{service_line}\n\n"
        "【必办（先做，按业务匹配）】\n"
        f"{permit_catalog}\n"
        "说明：以上属于强制准入许可清单，按业务匹配办理，不是要求一次性全部都办。\n"
        "同时需做基础合规准备：主体经营范围、厂房分区、设备、检验能力、人员与制度文件。\n\n"
        "【建议（第二阶段）】\n"
        f"{suggestion_line}\n"
        "2) 企业管理咨询（流程优化/成本与效率）可在拿证路径明确后并行规划。\n\n"
        "【暂不优先】\n"
        f"{not_priority_line}\n\n"
        "如果您愿意，我可以下一步按您的产品类别和经营模式，给您出一版“必办许可清单+办理顺序+资料清单+预计时间表”（以当地最新监管要求为准）。"
    )


def _build_ton_bag_export_fix_reply():
    return (
        "您这轮问题是“吨袋产品出海”，应按出口合规路径处理，不走食品许可路径。\n\n"
        "【先确认（必须）】\n"
        "1) 目标国家/地区（不同市场要求不同）。\n"
        "2) 产品用途与装载物（普通货物还是危险品）。\n"
        "3) 客户或平台要求的标准与检测项目。\n\n"
        "【出海基础动作】\n"
        "1) 建立产品技术资料包：规格书、材质说明、质检记录、可追溯信息。\n"
        "2) 按目标市场做检测与合规文件（按国家和用途匹配，不是一套证走天下）。\n"
        "3) 若涉及危险品运输场景，补充对应运输包装性能与合规要求。\n"
        "4) 同步准备贸易与交付资料（合同条款、标签、报关单证等）。\n\n"
        "【不应默认】\n"
        "1) 不应默认套用食品生产许可（SC/QS）路径。\n"
        "2) 不应在未明确国家和用途前，直接给固定认证清单。\n\n"
        "如果您愿意，我可以按“目标国家 + 吨袋用途 + 年出货量”给您出一版出海合规清单和落地顺序。"
    )


def _build_ton_bag_export_prompt():
    return """
【话题切换规则（必须）】
- 用户本轮在问“吨袋/集装袋出海”，必须按出口合规路径回答。
- 忽略上一轮食品场景，不得沿用食品许可（SC/QS）话术。

【回答顺序（必须）】
1. 先确认目标国家、用途、装载物属性（是否危险品）。
2. 再给出出口基础动作：技术资料、检测/合规文件、贸易单证准备。
3. 最后给下一步动作（一次只追问1-2项关键字段）。

【禁止】
- 禁止默认推荐食品生产许可（SC/QS）和食品体系认证（ISO22000/HACCP）。
""".strip()


def _is_sc_condition_followup(user_message, history):
    normalized_user = _normalize(user_message)
    all_user_text = _normalize(_collect_user_text(history, user_message))
    asks_condition = _contains_any(normalized_user, CONDITION_QUESTION_KEYWORDS)
    in_sc_context = _contains_any(all_user_text, SC_CONTEXT_KEYWORDS)
    in_ton_bag_context = _contains_any(all_user_text, TON_BAG_EXPORT_KEYWORDS)
    return asks_condition and in_sc_context and not in_ton_bag_context


def _build_sc_condition_prompt():
    return """
【条件问题识别（必须）】
- 用户问“需要具备哪些条件/什么要求”且上下文已在食品办厂/SC许可场景，默认解释为“SC办理条件”。
- 不要重复“SC是强制”这类结论，直接回答“办理SC要满足什么”。

【回答结构（必须）】
1. 先一句确认：按“SC办理条件”回答。
2. 再分“硬件条件 / 人员条件 / 制度文件（软件） / 检验与质量控制 / 申报资料”给最小清单。
3. 最后给下一步动作（例如先做场地与平面分区评估）。

【禁止】
- 禁止把回答重心放在市场调研、营销、品牌策略。
""".strip()


def _build_sc_condition_fix_reply():
    return (
        "您这句“需要具备哪些条件”，我按“办理 SC 食品生产许可的条件”给您直接清单：\n\n"
        "【硬件条件】\n"
        "1) 合法且可用于食品生产的场地，生产区与生活区分开。\n"
        "2) 车间分区基本清晰（原辅料处理、生产加工、冷却/包装、成品贮存等），避免交叉污染。\n"
        "3) 具备匹配产能的设备设施，以及清洗、消毒、防虫防鼠等卫生设施。\n\n"
        "【人员条件】\n"
        "1) 关键岗位人员到位（含食品安全管理相关岗位）。\n"
        "2) 从业人员健康管理与培训记录齐全。\n\n"
        "【制度文件（软件条件）】\n"
        "1) 原料验收、生产过程控制、清洗消毒、留样、追溯与召回等制度。\n"
        "2) 对应台账/记录表单可落地执行（不是只写文件）。\n\n"
        "【检验与质量控制】\n"
        "1) 具备必要检验能力（可自建或委托有资质机构），并有相应安排与记录。\n"
        "2) 产品标准、过程控制点和出厂检验要求要对应起来。\n\n"
        "【申报资料（常见）】\n"
        "1) 主体资质与经营范围材料。\n"
        "2) 场地与平面布局、工艺流程、设备清单。\n"
        "3) 管理制度与记录样表、检验相关证明材料。\n\n"
        "以上以当地市场监管部门最新要求为准。"
        "如果您愿意，我可以下一步按您的卤味品类和计划产能，给您出一版“SC办理硬件+软件差距清单”和整改优先级。"
    )


def build_policy_prompt(user_message, history):
    all_user_text = _normalize(_collect_user_text(history, user_message))
    normalized_user = _normalize(user_message)
    has_identity_switch, previous_marker, current_marker = _detect_identity_switch(user_message, history)
    switch_prompt = _build_identity_switch_prompt(previous_marker, current_marker) if has_identity_switch else ""
    general_reasoning_prompt = _build_general_reasoning_prompt(user_message, history)
    is_contact_query = _is_contact_query(user_message)

    if is_contact_query:
        if switch_prompt:
            return "\n".join([general_reasoning_prompt, switch_prompt, _build_contact_capture_prompt()])
        return "\n".join([general_reasoning_prompt, _build_contact_capture_prompt()])

    has_ton_bag_current = _contains_any(normalized_user, TON_BAG_EXPORT_KEYWORDS)
    has_export_current = _contains_any(normalized_user, EXPORT_SCENARIO_KEYWORDS)
    has_food_current = _contains_any(normalized_user, FOOD_FACTORY_KEYWORDS)
    if has_ton_bag_current and has_export_current and not has_food_current:
        if switch_prompt:
            return "\n".join([general_reasoning_prompt, switch_prompt, _build_ton_bag_export_prompt()])
        return "\n".join([general_reasoning_prompt, _build_ton_bag_export_prompt()])

    if _is_sc_condition_followup(user_message, history):
        if switch_prompt:
            return "\n".join([general_reasoning_prompt, switch_prompt, _build_sc_condition_prompt()])
        return "\n".join([general_reasoning_prompt, _build_sc_condition_prompt()])

    in_production_scenario = _contains_any(all_user_text, PRODUCTION_SCENARIO_KEYWORDS)
    matched_tracks = _detect_permit_tracks(all_user_text)
    permit_catalog_for_prompt = _format_permit_catalog(matched_tracks)
    asks_ambiguous_process = _contains_any(normalized_user, AMBIGUOUS_PROCESS_KEYWORDS)
    asks_diy_recipe = _contains_any(normalized_user, DIY_RECIPE_HINTS)
    asks_management_specific = _contains_any(
        normalized_user,
        ["市场调研", "渠道", "获客", "营销", "品牌", "定价", "管理", "组织", "绩效"],
    )

    # 对“具体怎么弄/怎么办”这种短句，在咨询场景默认按“办理流程”解释，避免跑去讲制作教程
    if asks_ambiguous_process and not asks_diy_recipe:
        if in_production_scenario:
            return "\n".join(
                [
                    general_reasoning_prompt,
                    "【歧义消解规则（必须）】",
                    "- 用户说“具体怎么弄/怎么做/怎么办”时，在本咨询场景默认解释为“办理流程怎么走”，不是配方或制作教程。",
                    "- 若本轮是追问，必须延续上一轮结论，不要重新从市场调研起盘。",
                    "- 默认先回答“生产许可/认证/企业管理咨询路径”，除非用户明确指定只问市场策略或配方。",
                    "- 先给生产许可前置清单（按业务匹配，不要求全部办理）：",
                    permit_catalog_for_prompt,
                    "- 禁止输出食品制作步骤（如原料、饼皮、馅料、烘烤、模具等）。",
                ]
            )
        return "\n".join(
            [
                general_reasoning_prompt,
                "【歧义消解规则（必须）】",
                "- 用户说“具体怎么弄/怎么做/怎么办”时，默认按“业务办理流程”回答。",
                "- 默认先回答信义可提供的生产许可/认证/管理咨询路径。",
                "- 禁止输出与本公司业务无关的DIY制作教程。",
            ]
        )

    if not in_production_scenario:
        if switch_prompt:
            return "\n".join([general_reasoning_prompt, switch_prompt])
        return general_reasoning_prompt

    asks_permit = _contains_any(all_user_text, PERMIT_KEYWORDS)
    asks_in_cert_context = _contains_any(all_user_text, CERT_SERVICE_CONTEXT_KEYWORDS)
    is_mooncake_like = _contains_any(all_user_text, ["月饼", "糕点", "烘焙"])
    mentions_export = _contains_any(all_user_text, ["出口", "欧盟", "海外", "外贸", "ce", "fda"])

    must_first = "当前客户是“生产/办厂”场景，必须优先解决“合规准入与生产许可”，再谈经营建议和体系认证。"
    ordering = """
【生产场景回答顺序（必须遵守）】
1. 第一段先给“先办什么许可”的结论：生产许可类事项属于前置强制准入。
2. 第二段解释“为什么”：说明不办理对应许可通常无法合规生产或上市销售。
3. 第三段给“按业务匹配的许可清单”，强调“按场景匹配，不是一次全部办理”。
4. 第四段给“最小可执行清单”：前置条件、关键材料、办理路径、预计周期影响因素。
5. 最后再补充可选提升项（如ISO体系/管理咨询），明确“第二阶段优化，不是首要前置”。
"""
    guardrails = """
【行业约束】
- 生产许可类为强制准入兜底，优先级高于体系认证和泛经营建议。
- 许可兜底清单（按业务匹配）：QS 食品相关产品生产许可、SC 食品生产许可、医疗器械经营/生产许可证、特种设备设计/制造/安装许可证、保健食品许可证、化妆品许可证、消毒产品卫生许可证、排水/排污许可证。
- 当用户说“怎么弄好/怎么办”，在本场景下要理解为“先做哪些许可和认证”，不能先给泛商业建议。
- 禁止输出食品制作步骤（如原料、配方、饼皮、馅料、烘烤、模具等）作为主回答。
- 默认身份是“信义咨询顾问”：先回答可办理的生产许可/认证/管理咨询路径，再补充经营建议。
- 涉及地方监管细则时，明确提示“以当地市场监管部门最新要求为准”。
"""
    permit_catalog_block = f"""
【本轮许可匹配清单（优先输出）】
{permit_catalog_for_prompt}
"""
    answer_template = """
【输出模板（强制）】
请按“必办/建议/暂不优先”三段输出：
- 必办（先做）：先列“生产许可类”并写清“证件名称 + 是否强制 + 原因 + 不办的后果”。
- 建议（第二阶段）：写清“适用场景 + 价值”，不要包装成强制项。
- 暂不优先：明确哪些证不是当前默认前置，避免误导和过度办理。
"""
    closing = """
【销售推进要求】
- 回答后必须给一个下一步动作，且一次只追问1-2个关键信息（如产品类别、是否自产、计划产能）。
- 示例：
  “如果您愿意，我可以先按‘月饼自产’给您列一版SC办理资料清单和预计时间表。”
"""
    if asks_permit:
        direct_answer = """
【本轮优先】
- 用户在问“是否需要许可证”，第一句必须直接回答“需要先办理对应生产许可，属于前置强制准入”。
- 然后给出与业务匹配的许可清单，不要直接抛市场调研。
"""
    elif asks_ambiguous_process:
        direct_answer = """
【本轮优先】
- 用户问“具体怎么弄”，第一句先讲“先办生产许可，再谈经营策略”，禁止先讲市场调研。
- 这是对上一轮的追问，必须承接上一轮已给结论，不得重启话题。
"""
    elif asks_management_specific:
        direct_answer = """
【本轮优先】
- 用户虽提到经营管理话题，也要先用1-2句交代生产许可前置，再回答管理建议。
"""
    elif asks_in_cert_context:
        direct_answer = """
【本轮优先】
- 用户已明确来咨询认证/许可，第一段不要泛讲市场调研，先回答“先办什么证、为什么、顺序”。
"""
    else:
        direct_answer = ""

    mooncake_rule = ""
    if is_mooncake_like:
        mooncake_rule = """
【月饼/糕点专用约束】
- 默认场景按“国内生产销售”解释：先讲SC生产许可与食品合规，不默认抛出CCC。
- 仅当用户明确“出口”时，才补充出口目的地相关认证（如CE/FDA等）与备案要求。
"""

    export_rule = ""
    if not mentions_export:
        export_rule = "【出口处理】用户未提及出口，不主动展开海外认证清单。"

    return "\n".join(
        [
            general_reasoning_prompt,
            switch_prompt,
            must_first,
            ordering,
            guardrails,
            permit_catalog_block,
            answer_template,
            mooncake_rule,
            export_rule,
            direct_answer,
            closing,
        ]
    ).strip()


def enforce_policy_reply(user_message, history, assistant_reply):
    reply = (assistant_reply or "").strip()
    if not reply:
        return reply

    if _is_contact_query(user_message):
        normalized_reply = _normalize(reply)
        has_lead_capture = _contains_any(normalized_reply, CONTACT_LEAD_CAPTURE_HINTS)
        has_direct_contact = ("13676797588" in normalized_reply) or ("87333310@qq.com" in normalized_reply)
        if not has_lead_capture or not has_direct_contact:
            return _build_contact_capture_fix_reply()

    if _is_sc_condition_followup(user_message, history):
        normalized_reply = _normalize(reply)
        has_condition_details = _contains_any(normalized_reply, SC_CONDITION_REPLY_HINTS)
        if not has_condition_details:
            return _build_sc_condition_fix_reply()
        first_generic_pos = _find_first_hit_pos(normalized_reply, GENERIC_BUSINESS_HINTS)
        first_condition_pos = _find_first_hit_pos(normalized_reply, SC_CONDITION_REPLY_HINTS)
        if first_generic_pos >= 0 and (first_condition_pos < 0 or first_generic_pos < first_condition_pos):
            return _build_sc_condition_fix_reply()

    normalized_user = _normalize(user_message)
    has_identity_switch, _, _ = _detect_identity_switch(user_message, history)
    is_followup = _is_followup_question(user_message, history)

    if has_identity_switch:
        normalized_reply = _normalize(reply)
        has_clarify = _contains_any(normalized_reply, CLARIFY_REPLY_HINTS)
        previous_domain = _get_previous_user_domain(history)
        current_domain = _detect_domain(user_message)
        old_domain_hit = _contains_any(normalized_reply, _domain_reply_hints(previous_domain))
        new_domain_hit = _contains_any(normalized_reply, _domain_reply_hints(current_domain))
        if not has_clarify or (old_domain_hit and not new_domain_hit):
            return _build_identity_switch_fix_reply(user_message)

    if is_followup and _looks_like_generic_restart(reply):
        return _build_followup_alignment_fix_reply(user_message, history)

    if _contains_any(normalized_user, TON_BAG_EXPORT_KEYWORDS) and _contains_any(normalized_user, EXPORT_SCENARIO_KEYWORDS):
        normalized_reply = _normalize(reply)
        if _contains_any(normalized_reply, FOOD_REPLY_HINTS):
            return _build_ton_bag_export_fix_reply()
        return reply

    all_user_text = _normalize(_collect_user_text(history, user_message))
    if not _contains_any(all_user_text, PRODUCTION_SCENARIO_KEYWORDS):
        return reply

    normalized_reply = _normalize(reply)
    hit_count = 0
    for keyword in RECIPE_ANSWER_HINTS:
        if keyword in normalized_reply:
            hit_count += 1

    generic_hit_count = 0
    for keyword in GENERIC_BUSINESS_HINTS:
        if keyword in normalized_reply:
            generic_hit_count += 1

    has_permit_signal = _contains_any(normalized_reply, PERMIT_RESPONSE_HINTS)
    is_process_question = _contains_any(_normalize(user_message), AMBIGUOUS_PROCESS_KEYWORDS)
    asks_permit = _contains_any(all_user_text, PERMIT_KEYWORDS)
    first_generic_pos = _find_first_hit_pos(normalized_reply, GENERIC_BUSINESS_HINTS)
    first_permit_pos = _find_first_hit_pos(normalized_reply, PERMIT_RESPONSE_HINTS)

    if hit_count >= 2:
        return _build_permit_first_fix_reply(user_message, history)
    if (generic_hit_count >= 2 and not has_permit_signal) or (is_process_question and not has_permit_signal):
        return _build_permit_first_fix_reply(user_message, history)
    if is_process_question and generic_hit_count >= 1:
        if first_permit_pos < 0 or (first_generic_pos >= 0 and first_generic_pos < first_permit_pos):
            return _build_permit_first_fix_reply(user_message, history)
    if asks_permit and not has_permit_signal:
        return _build_permit_first_fix_reply(user_message, history)

    return reply
