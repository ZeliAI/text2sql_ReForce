from dataclasses import dataclass
from datetime import date, timedelta
from typing import Optional


@dataclass(frozen=True)
class DateAdjustResult:
    question: str
    note: str


def adjust_question_dates(question: str, today: Optional[date] = None) -> DateAdjustResult:
    today = today or date.today()
    replacements = {
        "今天": today.isoformat(),
        "昨日": (today - timedelta(days=1)).isoformat(),
        "昨天": (today - timedelta(days=1)).isoformat(),
        "近7天": f"{(today - timedelta(days=7)).isoformat()} 至 {today.isoformat()}",
        "最近7天": f"{(today - timedelta(days=7)).isoformat()} 至 {today.isoformat()}",
        "近30天": f"{(today - timedelta(days=30)).isoformat()} 至 {today.isoformat()}",
        "最近30天": f"{(today - timedelta(days=30)).isoformat()} 至 {today.isoformat()}",
    }
    adjusted = question
    applied = []
    for source, target in replacements.items():
        if source in adjusted:
            adjusted = adjusted.replace(source, target)
            applied.append(f"{source}->{target}")
    if not applied:
        return DateAdjustResult(question=question, note="未识别到需要显式改写的相对日期。")
    return DateAdjustResult(question=adjusted, note="；".join(applied))
