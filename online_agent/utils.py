import json
import re
from pathlib import Path
from typing import Any


def load_jsonl(path: Path) -> list[dict[str, Any]]:
    return [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line.strip()]


def extract_sql(text: str) -> str:
    text = text.strip()
    matches = re.findall(r"```sql\s*(.*?)```", text, flags=re.IGNORECASE | re.DOTALL)
    if matches:
        return matches[-1].strip().rstrip(";") + ";"
    if re.match(r"(?is)^sql\s*\n", text):
        text = re.sub(r"(?is)^sql\s*\n", "", text, count=1).strip()
    if text.startswith("--") and "目前用户查询无法满足" in text:
        return text.rstrip(";") + ";"
    sql_match = re.search(r"(?is)\b(?:with|select)\b.*?(?:;|$)", text)
    if sql_match:
        return sql_match.group(0).strip().rstrip(";") + ";"
    return ""


def extract_selected_candidate(text: str, candidate_count: int) -> int:
    patterns = [
        r"\[selected_candidate\]\s*(?:candidate_)?(\d+)",
        r"selected_candidate\s*[:：]\s*(?:candidate_)?(\d+)",
        r"候选\s*(\d+)",
        r"candidate_(\d+)",
    ]
    for pattern in patterns:
        match = re.search(pattern, text, flags=re.IGNORECASE)
        if match:
            selected = int(match.group(1))
            if 1 <= selected <= candidate_count:
                return selected
    return 0


def select_by_validation(candidates: list[dict[str, Any]]) -> int:
    status_rank = {"pass": 0, "warning": 1, "fail": 2}
    scored = []
    for index, candidate in enumerate(candidates):
        validation = candidate["validation"]
        scored.append(
            (
                status_rank.get(validation["status"], 3),
                validation["error_count"],
                validation["warning_count"],
                len(candidate["sql"]),
                index,
            )
        )
    return min(scored)[-1]
