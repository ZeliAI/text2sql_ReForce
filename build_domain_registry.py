import argparse
import json
import re
from pathlib import Path
from typing import Any

from online_agent.markdown_utils import extract_sql_blocks, iter_markdown_tables, parse_values_from_description


REPO_ROOT = Path(__file__).resolve().parent


DEFAULT_OUTPUT_DIR = REPO_ROOT / "data" / "domain_registries"


DOMAIN_DEFAULTS = {
    "marketing": {
        "name": "投放域",
        "doc_dir": REPO_ROOT / "data" / "投放域表合并",
        "overview_patterns": ["*Schema*总览*.md"],
        "join_rule": "优先使用 DWS 汇总表；仅当需要用户级明细或明细字段时使用 DWD，并按业务外键关联 DIM 表。",
        "dt_rule": "所有投放域查询必须过滤 dt 分区；线上环境优先补充 environment = 'R'。",
    },
    "push": {
        "name": "push域",
        "doc_dir": REPO_ROOT / "data" / "push域表合并",
        "overview_patterns": ["*Schema*总览*.md"],
        "join_rule": "优先使用 ADS / DWS 汇总表；任务详情使用核心 DWD 宽表；曝光/点击明细按 delivery_push_task_id 关联任务表。",
        "dt_rule": "所有 push 域查询必须过滤 dt 分区；线上环境优先补充 environment = 'R'。",
    },
}


def clean_full_name(value: str) -> str:
    value = value.strip()
    if value.startswith("odps.sg."):
        return value.removeprefix("odps.sg.")
    return value


def key_value_info(tables: list[dict[str, Any]]) -> dict[str, str]:
    result: dict[str, str] = {}
    for table in tables:
        headers = table["headers"]
        if len(headers) < 2:
            continue
        if headers[:2] not in (["属性", "值"], ["项目", "内容"]):
            continue
        for row in table["rows"]:
            if len(row) >= 2:
                result[row[0]] = row[1]
    return result


def first_non_empty(*values: str) -> str:
    for value in values:
        if value:
            return value
    return ""


def normalize_header(value: str) -> str:
    value = re.sub(r"[*`]", "", value).strip()
    value = re.sub(r"\s+", "", value)
    return value


def normalized_index(headers: list[str]) -> dict[str, int]:
    return {normalize_header(header): pos for pos, header in enumerate(headers)}


def row_value(row: list[str], idx: dict[str, int], key: str) -> str:
    pos = idx.get(key)
    if pos is None or len(row) <= pos:
        return ""
    return row[pos]


def parse_columns(path: Path, tables: list[dict[str, Any]]) -> list[dict[str, Any]]:
    columns = []
    for table in tables:
        headers = table["headers"]
        if "字段名" not in headers:
            continue
        idx = normalized_index(headers)
        for row in table["rows"]:
            if len(row) <= idx["字段名"]:
                continue
            column_name = row[idx["字段名"]].strip()
            if not column_name or column_name == "字段名":
                continue
            description = first_non_empty(
                row_value(row, idx, "描述"),
                row_value(row, idx, "说明"),
            )
            value_hints_text = first_non_empty(
                row_value(row, idx, "值域/示例"),
                row_value(row, idx, "使用方式"),
            )
            columns.append(
                {
                    "name": column_name,
                    "cn_name": description,
                    "type": row_value(row, idx, "类型"),
                    "description": "；".join(part for part in [description, value_hints_text] if part),
                    "value_hints": parse_values_from_description(value_hints_text or description),
                    "source": {"file": path.name, "line_start": table["line_start"]},
                }
            )
    return columns


def extract_doc_description(text: str, info: dict[str, str]) -> str:
    if info.get("描述"):
        return info["描述"]
    if info.get("说明"):
        return info["说明"]
    title = re.search(r"^#\s+(.+)$", text, flags=re.MULTILINE)
    return title.group(1).strip() if title else ""


def parse_table_doc(path: Path) -> dict[str, Any]:
    text = path.read_text(encoding="utf-8")
    tables = iter_markdown_tables(path)
    info = key_value_info(tables)
    table_name = path.stem
    table_name = re.sub(r"^(投放域|PUSH域|push域)_\d+_", "", table_name, flags=re.IGNORECASE)
    full_name = clean_full_name(info.get("完整路径", ""))
    if not full_name:
        full_name = table_name
    table_short_name = full_name.split(".")[-1]
    partition = info.get("分区", "")
    partition_match = re.search(r"\b(dt|hh)\b", partition, flags=re.IGNORECASE)
    return {
        "table_name": table_short_name,
        "database": ".".join(full_name.split(".")[:-1]),
        "full_name": full_name,
        "layer": info.get("层级", ""),
        "description": extract_doc_description(text, info),
        "partition_field": partition_match.group(1).lower() if partition_match else "dt",
        "join_keys": extract_join_keys(info),
        "columns": parse_columns(path, tables),
        "examples": extract_sql_blocks(text),
        "source": {"file": path.name},
    }


def extract_join_keys(info: dict[str, str]) -> list[str]:
    keys = []
    for key, value in info.items():
        if "外键" not in key:
            continue
        left = re.split(r"→|->", value)[0]
        for token in re.findall(r"\b[a-zA-Z_][a-zA-Z0-9_]*\b", left):
            keys.append(token)
    return sorted(set(keys))


def extract_domain_description(text: str) -> str:
    match = re.search(r"##\s*一、域说明\s*(.*?)(?:\n## |\Z)", text, flags=re.DOTALL)
    if not match:
        return ""
    block = re.sub(r"\n+", "\n", match.group(1)).strip()
    block = re.sub(r"\*\*", "", block)
    return block


def parse_concepts(table: dict[str, Any]) -> list[dict[str, Any]]:
    headers = [normalize_header(header) for header in table["headers"]]
    if "概念" not in headers or "说明" not in headers:
        return []
    idx = normalized_index(table["headers"])
    concepts = []
    for row in table["rows"]:
        concept = row_value(row, idx, "概念")
        if not concept:
            continue
        concepts.append(
            {
                "concept": concept,
                "en_name": row_value(row, idx, "英文"),
                "description": row_value(row, idx, "说明"),
                "related_table": row_value(row, idx, "关联表"),
                "source": {"file": table["source_file"], "line_start": table["line_start"]},
            }
        )
    return concepts


def parse_table_selection_rules(table: dict[str, Any]) -> list[dict[str, Any]]:
    headers = [normalize_header(header) for header in table["headers"]]
    if "场景" not in headers or "使用表" not in headers:
        return []
    idx = normalized_index(table["headers"])
    rules = []
    for row in table["rows"]:
        scenario = row_value(row, idx, "场景")
        if not scenario:
            continue
        rules.append(
            {
                "scenario": scenario,
                "table": row_value(row, idx, "使用表"),
                "reason": row_value(row, idx, "理由"),
                "source": {"file": table["source_file"], "line_start": table["line_start"]},
            }
        )
    return rules


def parse_business_term_table(table: dict[str, Any]) -> list[dict[str, Any]]:
    idx = normalized_index(table["headers"])
    term_key = "用户说的"
    if term_key not in idx:
        return []

    target_key = ""
    for key in idx:
        if key == term_key:
            continue
        if (
            "SQL写法" in key
            or "对应写法" in key
            or "实际值" in key
            or "dt条件" in key
            or key in {"space_name实际值", "字段", "说明"}
        ):
            target_key = key
            break
    if not target_key:
        return []

    terms = []
    field_name = ""
    actual_value_match = re.match(r"(.+?)实际值$", target_key)
    if actual_value_match:
        field_name = actual_value_match.group(1)

    for row in table["rows"]:
        term = row_value(row, idx, term_key)
        mapped_value = row_value(row, idx, target_key)
        if not term or not mapped_value:
            continue
        if field_name:
            sql = f"{field_name} = '{mapped_value}'"
        elif target_key == "space_name实际值":
            sql = f"space_name = '{mapped_value}'"
        else:
            sql = mapped_value
        terms.append(
            {
                "term": term,
                "sql": sql,
                "field": field_name,
                "mapped_value": mapped_value,
                "source": {"file": table["source_file"], "line_start": table["line_start"]},
            }
        )
    return terms


def parse_overview(path: Path) -> dict[str, Any]:
    text = path.read_text(encoding="utf-8")
    domain_description = extract_domain_description(text)
    table_list = []
    metrics = []
    business_terms = []
    concepts = []
    table_selection_rules = []
    for table in iter_markdown_tables(path):
        headers = table["headers"]
        normalized_headers = [normalize_header(header) for header in headers]
        if "表名" in normalized_headers and ("说明" in normalized_headers or "核心能力" in normalized_headers):
            idx = normalized_index(headers)
            for row in table["rows"]:
                if len(row) <= idx["表名"]:
                    continue
                table_list.append(
                    {
                        "table_name": row[idx["表名"]],
                        "layer": row_value(row, idx, "层级"),
                        "description": first_non_empty(
                            row_value(row, idx, "说明"),
                            row_value(row, idx, "核心能力"),
                        ),
                        "source": {"file": path.name, "line_start": table["line_start"]},
                    }
                )
        if "指标名称" in normalized_headers or "指标" in normalized_headers:
            idx = normalized_index(headers)
            name_key = "指标名称" if "指标名称" in idx else "指标"
            expression_key = ""
            for candidate in ["计算方式", "口径", "DWS计算公式", "DWD计算公式", "ADS计算公式"]:
                if candidate in idx:
                    expression_key = candidate
                    break
            for row in table["rows"]:
                if len(row) <= idx[name_key]:
                    continue
                metrics.append(
                    {
                        "name": row[idx[name_key]],
                        "expression": row[idx[expression_key]] if expression_key and len(row) > idx[expression_key] else "",
                        "description": row[2] if len(row) > 2 else "",
                        "source": {"file": path.name, "line_start": table["line_start"]},
                    }
                )
        concepts.extend(parse_concepts(table))
        table_selection_rules.extend(parse_table_selection_rules(table))
        business_terms.extend(parse_business_term_table(table))
    return {
        "domain_description": domain_description,
        "table_list": table_list,
        "metrics": metrics,
        "business_terms": business_terms,
        "concepts": concepts,
        "table_selection_rules": table_selection_rules,
        "examples": extract_sql_blocks(text),
    }


def build_field_index(registry: dict[str, Any]) -> dict[str, list[str]]:
    index: dict[str, list[str]] = {}
    for table in registry["tables"]:
        for column in table["columns"]:
            index.setdefault(column["name"], []).append(table["full_name"])
    return index


def build_compact_context(registry: dict[str, Any]) -> str:
    lines = [
        f"# {registry['domain']} Compact Schema Context",
        "",
        "## 全局规则",
        f"- JOIN 规则：{registry['global_rules']['join_rule']}",
        f"- dt 规则：{registry['global_rules']['dt_rule']}",
        "",
        "## 表与字段",
    ]
    for table in registry["tables"]:
        lines.append(f"### {table['full_name']}")
        lines.append(f"- 层级：{table.get('layer') or '未知'}")
        lines.append(f"- 用途：{table['description']}")
        fields = []
        for column in table["columns"][:120]:
            cn_name = f"（{column['cn_name']}）" if column["cn_name"] else ""
            fields.append(f"{column['name']}{cn_name}")
        lines.append("- 字段：" + "、".join(fields))
        lines.append("")
    if registry["business_terms"]:
        lines.extend(["## 常用业务术语映射"])
        for item in registry["business_terms"]:
            lines.append(f"- {item['term']} -> {item['sql']}")
        lines.append("")
    if registry.get("concepts"):
        lines.extend(["## 核心概念"])
        for item in registry["concepts"]:
            related = f"；关联表：{item['related_table']}" if item.get("related_table") else ""
            lines.append(f"- {item['concept']}：{item['description']}{related}")
        lines.append("")
    if registry.get("table_selection_rules"):
        lines.extend(["## 选表规则"])
        for item in registry["table_selection_rules"]:
            reason = f"；原因：{item['reason']}" if item.get("reason") else ""
            lines.append(f"- {item['scenario']} -> {item['table']}{reason}")
        lines.append("")
    if registry["metrics"]:
        lines.extend(["## 指标口径"])
        for item in registry["metrics"]:
            desc = f"；{item['description']}" if item.get("description") else ""
            lines.append(f"- {item['name']}：{item['expression']}{desc}")
    return "\n".join(lines).strip() + "\n"


def build_domain_registry(domain_key: str, doc_dir: Path, output_dir: Path, domain_name: str) -> dict[str, Any]:
    output_dir.mkdir(parents=True, exist_ok=True)
    defaults = DOMAIN_DEFAULTS.get(domain_key, {})
    overview_files = []
    for pattern in defaults.get("overview_patterns", ["*总览*.md"]):
        overview_files.extend(doc_dir.glob(pattern))
    overview_files = sorted(set(overview_files))
    overview = {
        "domain_description": "",
        "table_list": [],
        "metrics": [],
        "business_terms": [],
        "concepts": [],
        "table_selection_rules": [],
        "examples": [],
    }
    for overview_file in overview_files:
        parsed = parse_overview(overview_file)
        overview["domain_description"] = overview["domain_description"] or parsed["domain_description"]
        for key in ["table_list", "metrics", "business_terms", "concepts", "table_selection_rules", "examples"]:
            overview[key].extend(parsed[key])

    table_docs = []
    for path in sorted(doc_dir.glob("*.md")):
        if path in overview_files:
            continue
        table = parse_table_doc(path)
        if table["columns"]:
            table_docs.append(table)

    registry = {
        "domain": domain_name,
        "domain_key": domain_key,
        "version": "v1_2_rule_based_from_markdown",
        "source_dir": str(doc_dir),
        "domain_description": overview["domain_description"],
        "global_rules": {
            "join_rule": defaults.get("join_rule", ""),
            "dt_rule": defaults.get("dt_rule", ""),
        },
        "table_list": overview["table_list"],
        "tables": table_docs,
        "business_terms": overview["business_terms"],
        "concepts": overview["concepts"],
        "table_selection_rules": overview["table_selection_rules"],
        "metrics": overview["metrics"],
        "examples": overview["examples"],
    }
    registry["field_index"] = build_field_index(registry)

    registry_path = output_dir / f"{domain_key}_registry.json"
    registry_path.write_text(json.dumps(registry, ensure_ascii=False, indent=2), encoding="utf-8")
    context_path = output_dir / f"{domain_key}_compact_context.md"
    context_path.write_text(build_compact_context(registry), encoding="utf-8")
    log_path = output_dir / f"{domain_key}_registry_build_log.md"
    log_lines = [
        f"# {domain_name} registry build log",
        "",
        f"- source_dir: {doc_dir}",
        f"- table_count: {len(table_docs)}",
        f"- field_count: {sum(len(table['columns']) for table in table_docs)}",
        f"- business_term_count: {len(registry['business_terms'])}",
        f"- concept_count: {len(registry['concepts'])}",
        f"- table_selection_rule_count: {len(registry['table_selection_rules'])}",
        f"- metric_count: {len(registry['metrics'])}",
        "",
        "## Tables",
    ]
    for table in table_docs:
        log_lines.append(f"- {table['full_name']}：{len(table['columns'])} fields, source `{table['source']['file']}`")
    log_path.write_text("\n".join(log_lines) + "\n", encoding="utf-8")
    return {
        "domain": domain_name,
        "registry_path": str(registry_path),
        "context_path": str(context_path),
        "log_path": str(log_path),
        "table_count": len(table_docs),
        "field_count": sum(len(table["columns"]) for table in table_docs),
        "business_term_count": len(registry["business_terms"]),
        "concept_count": len(registry["concepts"]),
        "table_selection_rule_count": len(registry["table_selection_rules"]),
        "metric_count": len(registry["metrics"]),
    }


def main() -> None:
    parser = argparse.ArgumentParser(description="Build generic domain registries from business markdown docs.")
    parser.add_argument("--domain", choices=sorted(DOMAIN_DEFAULTS), required=True)
    parser.add_argument("--doc-dir", type=Path)
    parser.add_argument("--output-dir", type=Path, default=DEFAULT_OUTPUT_DIR)
    args = parser.parse_args()

    defaults = DOMAIN_DEFAULTS[args.domain]
    doc_dir = args.doc_dir or defaults["doc_dir"]
    result = build_domain_registry(args.domain, doc_dir, args.output_dir, defaults["name"])
    print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
