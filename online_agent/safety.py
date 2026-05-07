import re
from dataclasses import dataclass
from typing import Any


@dataclass(frozen=True)
class SafetyResult:
    status: str
    issues: list[dict[str, str]]
    sql: str


def _starts_with_unavailable(sql: str) -> bool:
    return sql.strip().startswith("--") and "目前用户查询无法满足" in sql


def apply_safety_guard(sql: str, validation: dict[str, Any], safety_config: dict[str, Any]) -> SafetyResult:
    issues: list[dict[str, str]] = []
    lowered = sql.lower()
    for keyword in safety_config.get("blocked_sql_keywords", []):
        if re.search(rf"\b{re.escape(keyword.lower())}\b", lowered):
            issues.append(
                {
                    "severity": "error",
                    "code": "BLOCKED_SQL_KEYWORD",
                    "message": f"线上链路禁止生成 {keyword.upper()} 类 SQL。",
                }
            )

    if safety_config.get("require_partition_filter", True) and not _starts_with_unavailable(sql):
        if "max_pt(" not in lowered and not re.search(r"\bdt\s*=", lowered):
            issues.append(
                {
                    "severity": "error",
                    "code": "MISSING_PARTITION_FILTER",
                    "message": "线上链路要求分区表必须带 dt / max_pt 分区过滤。",
                }
            )

    is_detail_query = bool(re.search(r"(?is)^\s*select\b", sql)) and not re.search(
        r"(?i)\b(count|sum|avg|min|max|group\s+by)\b", sql
    )
    if (
        safety_config.get("require_limit_for_detail_query", True)
        and is_detail_query
        and "limit" not in lowered
        and not _starts_with_unavailable(sql)
    ):
        default_limit = int(safety_config.get("default_limit", 1000))
        sql = sql.rstrip().rstrip(";") + f"\nLIMIT {default_limit};"
        issues.append(
            {
                "severity": "warning",
                "code": "DETAIL_QUERY_LIMIT_ADDED",
                "message": f"明细查询自动补充 LIMIT {default_limit}。",
            }
        )

    validation_status = validation.get("status", "fail")
    has_error = any(item["severity"] == "error" for item in issues)
    status = "fail" if has_error or validation_status == "fail" else ("warning" if issues or validation_status == "warning" else "pass")
    return SafetyResult(status=status, issues=issues, sql=sql)
