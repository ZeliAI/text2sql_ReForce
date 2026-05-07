from dataclasses import dataclass


SQL_INTENT_KEYWORDS = [
    "用户",
    "画像",
    "交易",
    "支付",
    "登录",
    "push",
    "投放",
    "曝光",
    "点击",
    "转化",
    "人数",
    "占比",
    "分布",
    "分析",
    "查询",
    "统计",
    "对比",
]


@dataclass(frozen=True)
class ClarifyResult:
    action: str
    message: str


def clarify_or_continue(question: str) -> ClarifyResult:
    normalized = question.strip().lower()
    if not normalized:
        return ClarifyResult(action="clarify", message="请补充你想查询的业务对象、指标和时间范围。")
    if "吃什么" in normalized or "午饭" in normalized or "中午" in normalized:
        return ClarifyResult(action="reject", message="这个问题不属于当前 Text2SQL 业务分析范围。")
    if "分析下用户画像" in normalized or normalized in {"用户画像", "画像分析"}:
        return ClarifyResult(
            action="clarify",
            message="请补充要分析的人群条件、指标口径和时间范围，例如生命周期、交易、登录或 push 行为。",
        )
    if not any(keyword.lower() in normalized for keyword in SQL_INTENT_KEYWORDS):
        return ClarifyResult(action="clarify", message="请补充需要查询的业务域、指标或筛选条件。")
    return ClarifyResult(action="continue", message="")
