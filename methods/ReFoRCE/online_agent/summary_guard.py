import re
from typing import Any


IGNORED_IDENTIFIERS = {
    "and",
    "as",
    "avg",
    "case",
    "count",
    "distinct",
    "else",
    "end",
    "from",
    "group",
    "in",
    "join",
    "like",
    "max_pt",
    "nullif",
    "on",
    "or",
    "order",
    "select",
    "string",
    "then",
    "where",
    "when",
    "with",
    "yyyy",
    "yyyymmdd",
}


def _strip_literals(text: str) -> str:
    text = re.sub(r"`([^`]*)`", r" \1 ", text)
    text = re.sub(r"'(?:''|[^'])*'", " ", text)
    return text


def registry_identifiers(registry: dict[str, Any]) -> tuple[set[str], set[str]]:
    fields = set()
    known = set()
    for table in registry.get("tables", []):
        full_name = table.get("full_name", "").lower()
        table_name = table.get("table_name", "").lower()
        if full_name:
            known.add(full_name)
            known.update(part for part in full_name.split(".") if part)
        if table_name:
            known.add(table_name)
        for column in table.get("columns", []):
            name = column.get("name", "").lower()
            if name:
                fields.add(name)
                known.add(name)
    return fields, known


def validate_schema_summary_fields(schema_summary: str, registry: dict[str, Any]) -> dict[str, Any]:
    fields, known = registry_identifiers(registry)
    text = _strip_literals(schema_summary)
    tokens = {
        token.lower()
        for token in re.findall(r"\b[a-zA-Z_][a-zA-Z0-9_]*\b", text)
        if "_" in token
    }
    unknown = sorted(token for token in tokens if token not in known and token not in IGNORED_IDENTIFIERS)
    return {
        "status": "pass" if not unknown else "fail",
        "unknown_fields": unknown,
        "known_field_count": len(fields),
        "message": ""
        if not unknown
        else "Schema Summary 引用了当前 registry 不存在的字段，已阻断 SQL 生成。",
    }
