import argparse
import json
import re
from pathlib import Path
from typing import Any


REPO_ROOT = Path(__file__).resolve().parents[2]
DEFAULT_MARKDOWN_DIR = REPO_ROOT / "data" / "业务评测集_markdown"
DEFAULT_OUTPUT_DIR = REPO_ROOT / "data" / "profile_eval"


TABLE_DOCS = [
    "画像域_02_adm_asap_base_user_label_dd.md",
    "画像域_03_adm_asap_algo_user_label_dd.md",
    "画像域_04_adm_asap_pay_user_label_dd.md",
    "画像域_05_adm_asap_other_action_user_label_dd.md",
]


def clean_cell(value: str) -> str:
    value = value.strip()
    if len(value) >= 2 and value[0] == value[-1] == '"':
        value = value[1:-1]
    return re.sub(r"<br\s*/?>", "\n", value, flags=re.IGNORECASE).strip()


def split_md_row(line: str) -> list[str]:
    cells = line.strip().strip("|").split("|")
    return [clean_cell(cell) for cell in cells]


def is_separator_row(cells: list[str]) -> bool:
    return all(re.fullmatch(r":?-{3,}:?", cell.strip()) for cell in cells if cell.strip())


def iter_markdown_tables(path: Path) -> list[dict[str, Any]]:
    lines = path.read_text(encoding="utf-8").splitlines()
    tables = []
    i = 0
    while i < len(lines):
        if not lines[i].lstrip().startswith("|"):
            i += 1
            continue

        start = i + 1
        raw_rows = []
        while i < len(lines) and lines[i].lstrip().startswith("|"):
            raw_rows.append(lines[i])
            i += 1

        parsed_rows = [split_md_row(row) for row in raw_rows]
        parsed_rows = [row for row in parsed_rows if row and not is_separator_row(row)]
        if not parsed_rows:
            continue

        headers, data_rows = parsed_rows[0], parsed_rows[1:]
        tables.append(
            {
                "source_file": path.name,
                "line_start": start,
                "headers": headers,
                "rows": data_rows,
            }
        )
    return tables


def current_section(lines: list[str], line_number: int) -> str:
    section = ""
    for line in lines[:line_number]:
        if line.startswith("#"):
            section = line.strip("# ").strip()
    return section


def parse_eval_set(markdown_path: Path) -> list[dict[str, Any]]:
    records = []
    for table in iter_markdown_tables(markdown_path):
        headers = table["headers"]
        if not headers or headers[0] != "序号":
            continue
        for row in table["rows"]:
            if len(row) < 7 or not re.fullmatch(r"U\d{3}", row[0]):
                continue
            records.append(
                {
                    "id": row[0],
                    "domain": "画像域",
                    "difficulty": row[1],
                    "question": row[2],
                    "expected_analysis": {
                        "semantic_mapping": row[3],
                        "table_selection": row[4],
                        "sql_complexity": row[5],
                        "score": int(row[6]) if row[6].isdigit() else row[6],
                    },
                    "source": {
                        "file": markdown_path.name,
                        "line_start": table["line_start"],
                    },
                }
            )
    return records


def parse_key_value_table(tables: list[dict[str, Any]], key_header: str, value_header: str) -> dict[str, str]:
    result = {}
    for table in tables:
        headers = table["headers"]
        if headers[:2] != [key_header, value_header]:
            continue
        for row in table["rows"]:
            if len(row) >= 2:
                result[row[0]] = row[1]
    return result


def extract_sql_blocks(text: str) -> list[str]:
    return [match.strip() for match in re.findall(r"```sql\s*(.*?)```", text, flags=re.DOTALL | re.IGNORECASE)]


def parse_values_from_description(description: str) -> list[str]:
    values = []
    for pattern in [
        r"'([^']+)'",
        r"（([^）]+)）",
        r"\(([^)]+)\)",
    ]:
        for match in re.findall(pattern, description):
            if ":" in match or "：" in match or "、" in match or "," in match:
                values.append(match.strip())
            elif pattern.startswith("'"):
                values.append(match.strip())
    seen = set()
    deduped = []
    for value in values:
        if value not in seen:
            seen.add(value)
            deduped.append(value)
    return deduped


def expand_compact_field_name(name: str) -> list[str]:
    name = name.strip()
    if " / " not in name:
        return [name]
    first, suffix = [part.strip() for part in name.split(" / ", 1)]
    if "_" not in first:
        return [first, suffix]
    prefix = first.rsplit("_", 1)[0]
    return [first, f"{prefix}_{suffix}"]


def normalize_overview_type(value: str) -> str:
    upper_value = value.upper()
    if upper_value in {"STRING", "BIGINT", "INT", "DECIMAL"}:
        return upper_value
    if value.lower() in {"string", "int", "decimal"}:
        return value.upper()
    return ""


def parse_table_doc(path: Path) -> dict[str, Any]:
    text = path.read_text(encoding="utf-8")
    tables = iter_markdown_tables(path)
    info = parse_key_value_table(tables, "项目", "内容")
    table_name = info.get("表名") or path.stem.removeprefix("画像域_02_").removeprefix("画像域_03_")
    database = info.get("库名", "")
    full_name = info.get("完整路径") or f"{database}.{table_name}".strip(".")

    columns = []
    for table in tables:
        headers = table["headers"]
        if "字段名" not in headers:
            continue
        idx = {header: pos for pos, header in enumerate(headers)}
        for row in table["rows"]:
            if len(row) <= idx["字段名"]:
                continue
            column_name = row[idx["字段名"]]
            if not column_name or column_name == "字段名":
                continue
            column = {
                "name": column_name,
                "cn_name": row[idx["字段中文名"]] if "字段中文名" in idx and len(row) > idx["字段中文名"] else "",
                "type": row[idx["字段类型"]] if "字段类型" in idx and len(row) > idx["字段类型"] else "",
                "description": row[idx["字段描述"]] if "字段描述" in idx and len(row) > idx["字段描述"] else "",
                "value_hints": [],
                "source": {
                    "file": path.name,
                    "line_start": table["line_start"],
                },
            }
            column["value_hints"] = parse_values_from_description(column["description"])
            columns.append(column)

    return {
        "table_name": table_name,
        "database": database,
        "full_name": full_name,
        "description": extract_table_description(text),
        "partition_field": "dt",
        "join_keys": ["user_id", "dt"],
        "columns": columns,
        "examples": extract_sql_blocks(text),
        "source": {"file": path.name},
    }


def extract_table_description(text: str) -> str:
    match = re.search(r"## 二、表描述\s*(.*?)(?:\n## |\Z)", text, flags=re.DOTALL)
    if not match:
        return ""
    return re.sub(r"\n+", "\n", match.group(1)).strip()


def parse_overview_core_fields(path: Path) -> dict[str, list[dict[str, Any]]]:
    lines = path.read_text(encoding="utf-8").splitlines()
    result: dict[str, list[dict[str, Any]]] = {}
    for table in iter_markdown_tables(path):
        headers = table["headers"]
        if "字段名" not in headers or not (("描述" in headers and "类型" in headers) or "值域/示例" in headers):
            continue

        section = current_section(lines, table["line_start"])
        table_match = re.search(r"(adm_asap_[a-z_]+_dd)", section)
        if not table_match:
            continue
        table_name = table_match.group(1)
        idx = {header: pos for pos, header in enumerate(headers)}
        for row in table["rows"]:
            if len(row) <= idx["字段名"]:
                continue
            raw_name = row[idx["字段名"]]
            for column_name in expand_compact_field_name(raw_name):
                description = row[idx["描述"]] if "描述" in idx and len(row) > idx["描述"] else ""
                value_text = row[idx["值域/示例"]] if "值域/示例" in idx and len(row) > idx["值域/示例"] else ""
                type_text = row[idx["类型"]] if "类型" in idx and len(row) > idx["类型"] else ""
                column = {
                    "name": column_name,
                    "cn_name": description,
                    "type": normalize_overview_type(type_text),
                    "description": "；".join(part for part in [description, value_text] if part),
                    "value_hints": parse_values_from_description(value_text),
                    "source": {"file": path.name, "line_start": table["line_start"]},
                }
                result.setdefault(table_name, []).append(column)
    return result


def parse_overview(path: Path) -> dict[str, Any]:
    text = path.read_text(encoding="utf-8")
    tables = iter_markdown_tables(path)
    table_list = []
    metrics = []
    business_terms = []
    for table in tables:
        headers = table["headers"]
        if headers[:4] == ["层级", "表名", "完整路径", "核心能力"]:
            for row in table["rows"]:
                if len(row) >= 5:
                    table_list.append(
                        {
                            "layer": row[0],
                            "table_name": row[1],
                            "full_name": row[2],
                            "capability": row[3],
                            "when_to_use": row[4],
                            "source": {"file": path.name, "line_start": table["line_start"]},
                        }
                    )
        elif headers[:2] == ["指标名称", "计算方式"]:
            for row in table["rows"]:
                if len(row) >= 2:
                    metrics.append(
                        {
                            "name": row[0],
                            "expression": row[1],
                            "description": row[2] if len(row) > 2 else "",
                            "source": {"file": path.name, "line_start": table["line_start"]},
                        }
                    )
        elif headers[:2] == ["用户说的", "SQL 写法"]:
            for row in table["rows"]:
                if len(row) >= 2:
                    business_terms.append(
                        {
                            "term": row[0],
                            "sql": row[1],
                            "source": {"file": path.name, "line_start": table["line_start"]},
                        }
                    )

    return {
        "source": {"file": path.name},
        "table_list": table_list,
        "join_rule": "4 张画像域表通过 user_id + dt JOIN，优先单表查询，只有跨表字段组合时才 JOIN。",
        "dt_rule": "所有查询必须指定 dt 分区；P0 默认使用 dt = max_pt('完整表名')，除非输入明确要求固定日期。",
        "metrics": metrics,
        "business_terms": business_terms,
        "core_fields": parse_overview_core_fields(path),
        "examples": extract_sql_blocks(text),
    }


def merge_overview_core_fields(table_docs: list[dict[str, Any]], overview: dict[str, Any]) -> int:
    added = 0
    for table in table_docs:
        existing = {column["name"] for column in table["columns"]}
        for column in overview["core_fields"].get(table["table_name"], []):
            if column["name"] in existing:
                continue
            table["columns"].append(column)
            existing.add(column["name"])
            added += 1
    return added


def build_field_index(registry: dict[str, Any]) -> dict[str, list[str]]:
    index: dict[str, list[str]] = {}
    for table in registry["tables"]:
        for column in table["columns"]:
            index.setdefault(column["name"], []).append(table["full_name"])
    return index


def extract_sql_identifiers(sql_text: str) -> set[str]:
    without_strings = re.sub(r"'[^']*'", " ", sql_text)
    tokens = set(re.findall(r"\b[a-zA-Z_][a-zA-Z0-9_]*\b", without_strings))
    keywords = {
        "AND",
        "AVG",
        "BETWEEN",
        "CASE",
        "COUNT",
        "DISTINCT",
        "ELSE",
        "END",
        "IN",
        "LIKE",
        "NULLIF",
        "OR",
        "THEN",
        "WHEN",
        "WHERE",
    }
    return {token for token in tokens if token.upper() not in keywords}


def validate_registry_refs(registry: dict[str, Any]) -> list[str]:
    fields = set(registry["field_index"])
    refs = set()
    for item in registry["business_terms"]:
        refs.update(extract_sql_identifiers(item["sql"]))
    for item in registry["metrics"]:
        refs.update(extract_sql_identifiers(item["expression"]))
    allowed_placeholders = {"xxx_prefer_level"}
    return sorted(ref for ref in refs if ref not in fields and ref not in allowed_placeholders)


def build_compact_context(registry: dict[str, Any]) -> str:
    lines = [
        "# 画像域 Compact Schema Context",
        "",
        "## 全局规则",
        f"- JOIN 规则：{registry['global_rules']['join_rule']}",
        f"- dt 规则：{registry['global_rules']['dt_rule']}",
        "- 用户数默认使用 COUNT(DISTINCT user_id)。",
        "",
        "## 表与字段",
    ]
    for table in registry["tables"]:
        lines.append(f"### {table['full_name']}")
        lines.append(f"- 用途：{table['description']}")
        field_text = []
        for column in table["columns"]:
            cn_name = f"（{column['cn_name']}）" if column["cn_name"] else ""
            field_text.append(f"{column['name']}{cn_name}")
        lines.append("- 字段：" + "、".join(field_text))
        lines.append("")

    lines.extend(["## 常用业务术语映射"])
    for item in registry["business_terms"]:
        lines.append(f"- {item['term']} -> {item['sql']}")
    lines.append("")

    lines.extend(["## 指标口径"])
    for item in registry["metrics"]:
        desc = f"；{item['description']}" if item.get("description") else ""
        lines.append(f"- {item['name']}：{item['expression']}{desc}")

    return "\n".join(lines).strip() + "\n"


def build_assets(markdown_dir: Path, output_dir: Path) -> dict[str, Any]:
    output_dir.mkdir(parents=True, exist_ok=True)

    eval_records = parse_eval_set(markdown_dir / "文档二_画像域Text2SQL评测集.md")
    eval_path = output_dir / "profile_text2sql_eval.jsonl"
    eval_path.write_text(
        "".join(json.dumps(record, ensure_ascii=False) + "\n" for record in eval_records),
        encoding="utf-8",
    )

    overview = parse_overview(markdown_dir / "画像域_01_Schema总览.md")
    table_docs = [parse_table_doc(markdown_dir / file_name) for file_name in TABLE_DOCS]
    overview_field_count = merge_overview_core_fields(table_docs, overview)
    registry = {
        "domain": "画像域",
        "version": "p0_rule_based_from_markdown",
        "source_dir": str(markdown_dir),
        "global_rules": {
            "join_rule": overview["join_rule"],
            "dt_rule": overview["dt_rule"],
            "default_metric": "用户数默认使用 COUNT(DISTINCT user_id)",
        },
        "table_list": overview["table_list"],
        "tables": table_docs,
        "business_terms": overview["business_terms"],
        "metrics": overview["metrics"],
    }
    registry["field_index"] = build_field_index(registry)
    unresolved_refs = validate_registry_refs(registry)

    registry_path = output_dir / "profile_schema_registry.json"
    registry_path.write_text(json.dumps(registry, ensure_ascii=False, indent=2), encoding="utf-8")

    context_path = output_dir / "profile_compact_context.md"
    context_path.write_text(build_compact_context(registry), encoding="utf-8")

    log_lines = [
        "# 画像域知识文档转化日志",
        "",
        f"- 评测集条数：{len(eval_records)}",
        f"- 表数量：{len(table_docs)}",
        f"- 字段数量：{sum(len(table['columns']) for table in table_docs)}",
        f"- 其中总览补充字段：{overview_field_count}",
        f"- 业务术语映射：{len(registry['business_terms'])}",
        f"- 指标口径：{len(registry['metrics'])}",
        f"- 未解析字段引用：{len(unresolved_refs)}",
        "",
        "## 表字段来源",
    ]
    for table in table_docs:
        log_lines.append(f"- {table['full_name']}：{len(table['columns'])} 个字段，来源 `{table['source']['file']}`")
    if unresolved_refs:
        log_lines.extend(["", "## 未解析字段引用", ""])
        for ref in unresolved_refs:
            log_lines.append(f"- `{ref}`")
    log_path = output_dir / "profile_schema_registry_build_log.md"
    log_path.write_text("\n".join(log_lines) + "\n", encoding="utf-8")

    return {
        "eval_path": eval_path,
        "registry_path": registry_path,
        "context_path": context_path,
        "log_path": log_path,
        "eval_count": len(eval_records),
        "table_count": len(table_docs),
        "field_count": sum(len(table["columns"]) for table in table_docs),
        "overview_field_count": overview_field_count,
        "unresolved_ref_count": len(unresolved_refs),
    }


def main() -> None:
    parser = argparse.ArgumentParser(description="Build profile-domain Text2SQL eval and schema assets from markdown docs.")
    parser.add_argument("--markdown-dir", type=Path, default=DEFAULT_MARKDOWN_DIR)
    parser.add_argument("--output-dir", type=Path, default=DEFAULT_OUTPUT_DIR)
    args = parser.parse_args()

    result = build_assets(args.markdown_dir, args.output_dir)
    print(json.dumps({key: str(value) for key, value in result.items()}, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
