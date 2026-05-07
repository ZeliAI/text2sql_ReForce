import re
from typing import Any


def compact_text(value: str, limit: int = 260) -> str:
    value = re.sub(r"\s+", " ", value or "").strip()
    return value if len(value) <= limit else value[: limit - 3] + "..."


def split_pieces(text: str) -> list[str]:
    return [piece for piece in re.split(r"[/（）()、,，;；\s]+", text or "") if piece]


def term_matches_question(term: str, question: str) -> bool:
    normalized = term.replace("用户", "")
    return term in question or (normalized and normalized in question) or any(piece in question for piece in split_pieces(term))


def extract_sql_identifiers(sql: str) -> set[str]:
    return {
        token.lower()
        for token in re.findall(r"\b[a-zA-Z_][a-zA-Z0-9_]*\b", sql or "")
    }


def table_name_variants(table: dict[str, Any]) -> set[str]:
    full_name = table.get("full_name", "")
    table_name = table.get("table_name", "")
    variants = {full_name, table_name}
    variants.update(part for part in full_name.split(".") if part)
    return {item for item in variants if item}


def score_table(
    question: str,
    table: dict[str, Any],
    business_terms: list[dict[str, Any]],
    metrics: list[dict[str, Any]],
    concepts: list[dict[str, Any]],
    selection_rules: list[dict[str, Any]],
) -> int:
    score = 0
    lowered_question = question.lower()
    variants = {item.lower() for item in table_name_variants(table)}
    if any(variant and variant in lowered_question for variant in variants):
        score += 5

    table_fields = {column.get("name", "").lower() for column in table.get("columns", []) if column.get("name")}
    for column in table.get("columns", []):
        name = column.get("name", "")
        if name and name.lower() in lowered_question:
            score += 4
        cn_name = column.get("cn_name") or ""
        if cn_name and any(piece and piece in question for piece in split_pieces(cn_name)):
            score += 1

    for term in business_terms:
        if not term_matches_question(term.get("term", ""), question):
            continue
        refs = extract_sql_identifiers(term.get("sql", ""))
        if refs & table_fields:
            score += 6
        elif term.get("field", "").lower() in table_fields:
            score += 6
        else:
            score += 2

    for metric in metrics:
        metric_name = metric.get("name", "")
        if not metric_name or not any(piece in question for piece in split_pieces(metric_name)):
            continue
        refs = extract_sql_identifiers(metric.get("expression", ""))
        if refs & table_fields:
            score += 7

    for concept in concepts:
        concept_name = concept.get("concept", "")
        if not concept_name or not any(piece in question for piece in split_pieces(concept_name)):
            continue
        related_table = (concept.get("related_table") or "").lower()
        if related_table and any(variant in related_table for variant in variants):
            score += 7

    for rule in selection_rules:
        scenario = rule.get("scenario", "")
        target_table = (rule.get("table") or "").lower()
        if not scenario or not any(piece and piece in question for piece in split_pieces(scenario)):
            continue
        if any(variant in target_table for variant in variants):
            score += 8

    return score


def choose_tables(question: str, registry: dict[str, Any], max_tables: int = 4) -> list[dict[str, Any]]:
    business_terms = registry.get("business_terms", [])
    metrics = registry.get("metrics", [])
    concepts = registry.get("concepts", [])
    selection_rules = registry.get("table_selection_rules", [])
    scored = [
        (score_table(question, table, business_terms, metrics, concepts, selection_rules), index, table)
        for index, table in enumerate(registry.get("tables", []))
    ]
    selected = [table for score, _, table in sorted(scored, key=lambda item: (-item[0], item[1])) if score > 0][:max_tables]
    if selected:
        return selected
    return registry.get("tables", [])[:max_tables]


def select_context(question: str, registry: dict[str, Any], max_columns_per_table: int = 80) -> dict[str, Any]:
    selected_tables = choose_tables(question, registry)
    matched_terms = [term for term in registry.get("business_terms", []) if term_matches_question(term.get("term", ""), question)]
    matched_metrics = [
        metric
        for metric in registry.get("metrics", [])
        if any(piece in question for piece in split_pieces(metric.get("name", "")))
    ]
    matched_concepts = [
        concept
        for concept in registry.get("concepts", [])
        if any(piece in question for piece in split_pieces(concept.get("concept", "")))
    ]

    selected_names = {table.get("full_name", "") for table in selected_tables}
    matched_rules = [
        rule
        for rule in registry.get("table_selection_rules", [])
        if any(full_name and full_name in (rule.get("table") or "") for full_name in selected_names)
        or any(piece and piece in question for piece in split_pieces(rule.get("scenario", "")))
    ]

    context_tables = []
    for table in selected_tables:
        context_tables.append(
            {
                "full_name": table.get("full_name", ""),
                "table_name": table.get("table_name", ""),
                "layer": table.get("layer", ""),
                "description": compact_text(table.get("description", "")),
                "partition_field": table.get("partition_field", "dt"),
                "join_keys": table.get("join_keys", []),
                "columns": [
                    {
                        "name": column.get("name", ""),
                        "cn_name": column.get("cn_name", ""),
                        "type": column.get("type", ""),
                        "description": compact_text(column.get("description", ""), 120),
                    }
                    for column in table.get("columns", [])[:max_columns_per_table]
                ],
                "examples": [compact_text(example, 240) for example in table.get("examples", [])[:2]],
            }
        )

    return {
        "domain": registry.get("domain", "当前域"),
        "domain_description": registry.get("domain_description", ""),
        "global_rules": registry.get("global_rules", {}),
        "tables": context_tables,
        "business_terms": matched_terms[:20] if matched_terms else registry.get("business_terms", [])[:20],
        "metrics": matched_metrics[:12] if matched_metrics else registry.get("metrics", [])[:12],
        "concepts": matched_concepts[:12] if matched_concepts else registry.get("concepts", [])[:10],
        "table_selection_rules": matched_rules[:8] if matched_rules else registry.get("table_selection_rules", [])[:6],
        "examples": [compact_text(example, 240) for example in registry.get("examples", [])[:4]],
    }


def render_context(context: dict[str, Any]) -> str:
    lines = [
        f"【主题域】{context['domain']}",
    ]
    if context.get("domain_description"):
        lines.append(f"【域说明】{compact_text(context['domain_description'], 400)}")
    lines.extend(
        [
            "",
            "【全局规则】",
            f"- JOIN：{context['global_rules'].get('join_rule', '无')}",
            f"- 分区：{context['global_rules'].get('dt_rule', '无')}",
        ]
    )
    default_metric = context["global_rules"].get("default_metric")
    if default_metric:
        lines.append(f"- 默认指标：{default_metric}")

    if context.get("concepts"):
        lines.extend(["", "【核心概念】"])
        for concept in context["concepts"]:
            related = f" / 关联表：{concept.get('related_table')}" if concept.get("related_table") else ""
            lines.append(f"- {concept.get('concept', '')}：{compact_text(concept.get('description', ''), 140)}{related}")

    if context.get("table_selection_rules"):
        lines.extend(["", "【选表规则】"])
        for rule in context["table_selection_rules"]:
            reason = f" / 理由：{compact_text(rule.get('reason', ''), 100)}" if rule.get("reason") else ""
            lines.append(f"- {rule.get('scenario', '')} -> {rule.get('table', '')}{reason}")

    lines.extend(["", "【相关表和字段】"])
    for table in context["tables"]:
        layer = f" / {table['layer']}" if table.get("layer") else ""
        join_keys = f" / join_keys={','.join(table['join_keys'])}" if table.get("join_keys") else ""
        lines.append(
            f"- {table['full_name']}{layer} / partition={table['partition_field']}{join_keys}：{table['description']}"
        )
        for column in table["columns"]:
            cn_name = f" / {column['cn_name']}" if column["cn_name"] else ""
            col_type = f" / {column['type']}" if column["type"] else ""
            desc = f" / {column['description']}" if column["description"] else ""
            lines.append(f"  - {column['name']}{cn_name}{col_type}{desc}")
        for example in table.get("examples", []):
            lines.append(f"  - example: {example}")

    if context.get("business_terms"):
        lines.extend(["", "【业务术语映射】"])
        for term in context["business_terms"]:
            lines.append(f"- {term.get('term', '')} -> {term.get('sql', '')}")

    if context.get("metrics"):
        lines.extend(["", "【指标口径】"])
        for metric in context["metrics"]:
            desc = f"；{metric.get('description')}" if metric.get("description") else ""
            lines.append(f"- {metric.get('name', '')}：{metric.get('expression', '')}{desc}")

    if context.get("examples"):
        lines.extend(["", "【参考 SQL 示例】"])
        for example in context["examples"]:
            lines.append(f"- {example}")

    return "\n".join(lines)


def build_compact_context(question: str, registry: dict[str, Any]) -> dict[str, Any]:
    context = select_context(question, registry)
    return {
        "context": context,
        "context_text": render_context(context),
        "context_tables": [table["full_name"] for table in context["tables"]],
    }
