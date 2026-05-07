import argparse
import json
import re
from pathlib import Path
from typing import Any


REPO_ROOT = Path(__file__).resolve().parents[2]
DEFAULT_REGISTRY_PATH = REPO_ROOT / "data" / "profile_eval" / "profile_schema_registry.json"


SQL_KEYWORDS = {
    "ALL",
    "AND",
    "AS",
    "ASC",
    "BETWEEN",
    "BY",
    "CASE",
    "CAST",
    "COUNT",
    "CURRENT_DATE",
    "DATEADD",
    "DATE_SUB",
    "DESC",
    "DISTINCT",
    "ELSE",
    "END",
    "FROM",
    "GROUP",
    "HAVING",
    "IN",
    "INNER",
    "IS",
    "JOIN",
    "LEFT",
    "LIKE",
    "LIMIT",
    "MAX_PT",
    "NOT",
    "NULL",
    "NULLIF",
    "ON",
    "OR",
    "ORDER",
    "OUTER",
    "RIGHT",
    "SELECT",
    "THEN",
    "UNION",
    "WHEN",
    "WHERE",
    "WITH",
}


SQL_FUNCTIONS = {
    "AVG",
    "COALESCE",
    "COUNT",
    "CURRENT_DATE",
    "DATEADD",
    "DATE_SUB",
    "MAX",
    "MAX_PT",
    "MIN",
    "ROUND",
    "SUM",
    "TO_CHAR",
    "TO_DATE",
}


def strip_strings(sql: str) -> str:
    return re.sub(r"'(?:''|[^'])*'", "''", sql)


def strip_comments(sql: str) -> str:
    sql = re.sub(r"--.*?$", "", sql, flags=re.MULTILINE)
    return re.sub(r"/\*.*?\*/", "", sql, flags=re.DOTALL)


def normalize_sql(sql: str) -> str:
    return re.sub(r"\s+", " ", strip_comments(sql)).strip()


def issue(severity: str, code: str, message: str, evidence: str = "") -> dict[str, str]:
    return {"severity": severity, "code": code, "message": message, "evidence": evidence}


def table_maps(registry: dict[str, Any]) -> tuple[dict[str, dict[str, Any]], dict[str, str], dict[str, set[str]]]:
    by_full_name = {table["full_name"].lower(): table for table in registry["tables"]}
    short_to_full = {table["table_name"].lower(): table["full_name"].lower() for table in registry["tables"]}
    fields_by_full = {
        table["full_name"].lower(): {column["name"].lower() for column in table["columns"]}
        for table in registry["tables"]
    }
    return by_full_name, short_to_full, fields_by_full


def parse_table_refs(sql: str, registry: dict[str, Any]) -> list[dict[str, str]]:
    by_full_name, short_to_full, _ = table_maps(registry)
    known_full = set(by_full_name)
    refs = []
    pattern = re.compile(
        r"(?is)\b(from|join)\s+([a-zA-Z_][\w]*\.[a-zA-Z_][\w]*|[a-zA-Z_][\w]*)\s*(?:as\s+)?([a-zA-Z_][\w]*)?"
    )
    for match in pattern.finditer(sql):
        raw_table = match.group(2)
        raw_alias = match.group(3)
        if raw_alias and raw_alias.upper() in SQL_KEYWORDS:
            raw_alias = None
        alias = raw_alias or raw_table.split(".")[-1]
        normalized = raw_table.lower()
        if normalized in known_full:
            full_name = normalized
        elif normalized in short_to_full:
            full_name = short_to_full[normalized]
        else:
            full_name = normalized
        refs.append({"table": raw_table, "full_name": full_name, "alias": alias, "kind": match.group(1).upper()})
    return refs


def parse_qualified_columns(sql: str) -> list[tuple[str, str]]:
    sql_no_strings = strip_strings(sql)
    return [
        (match.group(1), match.group(2))
        for match in re.finditer(r"\b([a-zA-Z_][\w]*)\.([a-zA-Z_][\w]*)\b", sql_no_strings)
        if match.group(2).lower() not in {"adm_asap_base_user_label_dd", "adm_asap_algo_user_label_dd", "adm_asap_pay_user_label_dd", "adm_asap_other_action_user_label_dd"}
    ]


def output_aliases(sql: str) -> set[str]:
    return {match.group(1).lower() for match in re.finditer(r"(?is)\bas\s+([a-zA-Z_][\w]*)", strip_strings(sql))}


def unqualified_identifiers(sql: str) -> set[str]:
    sql_no_strings = strip_strings(sql)
    sql_no_qualified = re.sub(r"\b[a-zA-Z_][\w]*\.[a-zA-Z_][\w]*\b", " ", sql_no_strings)
    return {token.lower() for token in re.findall(r"\b[a-zA-Z_][\w]*\b", sql_no_qualified)}


def validate_tables(table_refs: list[dict[str, str]], registry: dict[str, Any]) -> list[dict[str, str]]:
    by_full_name, _, _ = table_maps(registry)
    issues = []
    if not table_refs:
        issues.append(issue("error", "NO_TABLE", "SQL 中没有识别到 FROM / JOIN 表。"))
        return issues
    for ref in table_refs:
        if ref["full_name"] not in by_full_name:
            issues.append(issue("error", "UNKNOWN_TABLE", "SQL 使用了不属于画像域 registry 的表。", ref["table"]))
    return issues


def validate_columns(sql: str, table_refs: list[dict[str, str]], registry: dict[str, Any]) -> list[dict[str, str]]:
    _, _, fields_by_full = table_maps(registry)
    alias_to_full = {ref["alias"].lower(): ref["full_name"] for ref in table_refs}
    table_short_to_full = {ref["table"].split(".")[-1].lower(): ref["full_name"] for ref in table_refs}
    known_fields = set().union(*(fields_by_full.get(ref["full_name"], set()) for ref in table_refs)) if table_refs else set()
    known_aliases = set(alias_to_full) | set(table_short_to_full)
    ignored = {keyword.lower() for keyword in SQL_KEYWORDS | SQL_FUNCTIONS} | known_aliases | output_aliases(sql)
    ignored.update({"yyyyMMdd".lower(), "int", "string", "decimal"})
    ref_databases = set()
    ref_tables = set()
    for ref in table_refs:
        parts = ref["full_name"].split(".")
        if len(parts) == 2:
            ref_databases.add(parts[0])
            ref_tables.add(parts[1])
        else:
            ref_tables.add(ref["full_name"])

    issues = []
    for alias, column in parse_qualified_columns(sql):
        alias_key = alias.lower()
        column_key = column.lower()
        if alias_key not in alias_to_full and alias_key not in table_short_to_full:
            continue
        full_name = alias_to_full.get(alias_key) or table_short_to_full[alias_key]
        if column_key not in fields_by_full.get(full_name, set()):
            issues.append(
                issue(
                    "error",
                    "UNKNOWN_COLUMN_FOR_TABLE",
                    f"字段 `{column}` 不属于 `{full_name}`。",
                    f"{alias}.{column}",
                )
            )

    for token in sorted(unqualified_identifiers(sql) - ignored):
        if token in known_fields:
            continue
        if token in ref_databases:
            continue
        if token in ref_tables:
            continue
        # Unqualified output aliases inside ORDER BY are already removed by AS parsing; keep this conservative.
        if token.endswith("_cnt") or token.endswith("_ratio") or token.endswith("_rate"):
            continue
        issues.append(issue("error", "UNKNOWN_IDENTIFIER", "SQL 中出现了无法在当前相关表字段中确认的标识符。", token))
    return issues


def question_has_explicit_time(question: str) -> bool:
    return bool(re.search(r"昨天|前天|今日|今天|近\s*\d+\s*天|最近\s*\d+\s*天|\d{4}[-年]?\d{1,2}[-月]?\d{1,2}", question))


def validate_dt(sql: str, table_refs: list[dict[str, str]], question: str = "") -> list[dict[str, str]]:
    if not table_refs:
        return []
    sql_clean = normalize_sql(sql).lower()
    dt_condition_count = len(re.findall(r"(?:\b[a-zA-Z_][\w]*\.)?\bdt\s*=", sql_clean))
    issues = []
    if dt_condition_count == 0:
        issues.append(issue("error", "MISSING_DT", "所有画像域表都必须显式过滤 dt 分区。"))
    elif len(table_refs) > 1 and dt_condition_count < len(table_refs):
        issues.append(
            issue(
                "warning",
                "POSSIBLE_INCOMPLETE_DT",
                "多表 SQL 中 dt 过滤数量少于表引用数量，请确认每张表都在子查询或 WHERE 中过滤 dt。",
                f"dt 条件数={dt_condition_count}, 表引用数={len(table_refs)}",
            )
        )
    if not question_has_explicit_time(question):
        for ref in table_refs:
            full_name = re.escape(ref["full_name"])
            if not re.search(rf"max_pt\(\s*'{full_name}'\s*\)", sql_clean):
                issues.append(
                    issue(
                        "warning",
                        "MISSING_MAX_PT_FOR_TABLE",
                        "P0 默认建议每张表使用 dt = max_pt('完整表名')；如业务问题明确要求固定日期，可忽略此警告。",
                        ref["full_name"],
                    )
                )
    return issues


def validate_join_keys(sql: str, table_refs: list[dict[str, str]]) -> list[dict[str, str]]:
    if len(table_refs) <= 1:
        return []
    sql_clean = normalize_sql(sql).lower()
    user_join = re.search(r"\b[a-zA-Z_][\w]*\.user_id\s*=\s*[a-zA-Z_][\w]*\.user_id\b", sql_clean)
    dt_join = re.search(r"\b[a-zA-Z_][\w]*\.dt\s*=\s*[a-zA-Z_][\w]*\.dt\b", sql_clean)
    issues = []
    if not user_join:
        issues.append(issue("error", "MISSING_JOIN_USER_ID", "多表 JOIN 必须包含 user_id 等值关联。"))
    if not dt_join:
        issues.append(issue("error", "MISSING_JOIN_DT", "多表 JOIN 必须包含 dt 等值关联，避免跨分区误关联。"))
    return issues


def validate_count_distinct(sql: str, question: str = "") -> list[dict[str, str]]:
    sql_clean = normalize_sql(sql).lower()
    question_needs_user_count = bool(re.search(r"用户.*多少|多少.*用户|多少人|人数|用户数|分布|占比|比例", question))
    has_count = "count(" in sql_clean
    has_distinct_user = bool(re.search(r"count\s*\(\s*distinct\s+(?:[a-zA-Z_][\w]*\.)?user_id\s*\)", sql_clean))
    if question_needs_user_count and has_count and not has_distinct_user:
        return [issue("warning", "COUNT_WITHOUT_DISTINCT_USER", "画像域用户数默认应使用 COUNT(DISTINCT user_id)。")]
    return []


def validate_limit(sql: str, question: str = "") -> list[dict[str, str]]:
    if re.search(r"top\s*\d+|top\d+|前\s*\d+", question, flags=re.IGNORECASE) and not re.search(r"\blimit\s+\d+\b", sql, flags=re.IGNORECASE):
        return [issue("warning", "TOP_WITHOUT_LIMIT", "问题包含 topN / 前N 语义，但 SQL 未识别到 LIMIT。")]
    return []


def validate_unavailable(sql: str, table_refs: list[dict[str, str]]) -> list[dict[str, str]]:
    if "目前用户查询无法满足" in sql:
        return [issue("info", "UNAVAILABLE_OUTPUT", "SQL 明确输出了无法满足说明。")]
    if sql.strip().startswith("--") and not table_refs:
        return [issue("warning", "COMMENT_ONLY_SQL", "SQL 只有注释，且没有标准无法满足说明。")]
    return []


def validate_sql(sql: str, registry: dict[str, Any], question: str = "") -> dict[str, Any]:
    table_refs = parse_table_refs(sql, registry)
    issues = []
    issues.extend(validate_unavailable(sql, table_refs))
    if "目前用户查询无法满足" not in sql:
        issues.extend(validate_tables(table_refs, registry))
        issues.extend(validate_columns(sql, table_refs, registry))
        issues.extend(validate_dt(sql, table_refs, question))
        issues.extend(validate_join_keys(sql, table_refs))
        issues.extend(validate_count_distinct(sql, question))
        issues.extend(validate_limit(sql, question))
    error_count = sum(item["severity"] == "error" for item in issues)
    warning_count = sum(item["severity"] == "warning" for item in issues)
    status = "pass" if error_count == 0 and warning_count == 0 else "warning" if error_count == 0 else "fail"
    return {
        "status": status,
        "error_count": error_count,
        "warning_count": warning_count,
        "table_refs": table_refs,
        "issues": issues,
    }


def render_validation_markdown(result: dict[str, Any]) -> str:
    status_cn = {"pass": "通过", "warning": "有警告", "fail": "失败"}.get(result["status"], result["status"])
    lines = [
        "# 静态 SQL 校验报告",
        "",
        f"- 状态：{status_cn}",
        f"- 错误数：{result['error_count']}",
        f"- 警告数：{result['warning_count']}",
        "",
        "## 表引用",
    ]
    if result["table_refs"]:
        for ref in result["table_refs"]:
            lines.append(f"- `{ref['table']}` alias `{ref['alias']}`")
    else:
        lines.append("- 未识别到表引用")
    lines.extend(["", "## 问题"])
    if result["issues"]:
        for item in result["issues"]:
            evidence = f"：`{item['evidence']}`" if item.get("evidence") else ""
            lines.append(f"- [{item['severity']}] {item['code']}：{item['message']}{evidence}")
    else:
        lines.append("- 未发现静态规则问题")
    return "\n".join(lines) + "\n"


def main() -> None:
    parser = argparse.ArgumentParser(description="Validate profile-domain ODPS SQL without executing data queries.")
    parser.add_argument("--sql-file", type=Path)
    parser.add_argument("--sql", default="")
    parser.add_argument("--question", default="")
    parser.add_argument("--registry", type=Path, default=DEFAULT_REGISTRY_PATH)
    parser.add_argument("--output-json", type=Path)
    parser.add_argument("--output-md", type=Path)
    args = parser.parse_args()

    sql = args.sql_file.read_text(encoding="utf-8") if args.sql_file else args.sql
    registry = json.loads(args.registry.read_text(encoding="utf-8"))
    result = validate_sql(sql, registry, args.question)
    print(json.dumps(result, ensure_ascii=False, indent=2))
    if args.output_json:
        args.output_json.parent.mkdir(parents=True, exist_ok=True)
        args.output_json.write_text(json.dumps(result, ensure_ascii=False, indent=2), encoding="utf-8")
    if args.output_md:
        args.output_md.parent.mkdir(parents=True, exist_ok=True)
        args.output_md.write_text(render_validation_markdown(result), encoding="utf-8")


if __name__ == "__main__":
    main()
