from dataclasses import dataclass


DOMAIN_KEYWORDS = {
    "profile": [
        "画像",
        "用户",
        "生命周期",
        "沉默",
        "回流",
        "交易",
        "支付",
        "登录",
        "push点击",
        "领券",
        "核销",
        "年龄",
        "性别",
    ],
    "marketing": [
        "投放",
        "广告",
        "营销位",
        "曝光",
        "点击",
        "转化",
        "素材",
        "行业",
        "任务",
    ],
    "push": [
        "push",
        "推送",
        "触达",
        "打开",
        "push任务",
        "push曝光",
        "push点击",
    ],
}


@dataclass(frozen=True)
class RouteResult:
    route_type: str
    domains: list[str]
    confidence: float
    reason: str


def route_question(question: str, default_domain: str = "profile") -> RouteResult:
    matched: dict[str, list[str]] = {}
    lowered = question.lower()
    for domain, keywords in DOMAIN_KEYWORDS.items():
        hits = [keyword for keyword in keywords if keyword.lower() in lowered]
        if hits:
            matched[domain] = hits

    if not matched:
        return RouteResult(
            route_type="single_domain",
            domains=[default_domain],
            confidence=0.35,
            reason=f"未命中明确域关键词，按当前调试默认域 {default_domain} 处理。",
        )

    domains = sorted(matched, key=lambda item: len(matched[item]), reverse=True)
    route_type = "mixed_domain" if len(domains) > 1 else "single_domain"
    reason = "；".join(f"{domain}: {','.join(hits[:5])}" for domain, hits in matched.items())
    confidence = min(0.95, 0.45 + 0.15 * sum(len(hits) for hits in matched.values()))
    return RouteResult(route_type=route_type, domains=domains, confidence=confidence, reason=reason)
