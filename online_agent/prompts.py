import re
from typing import Any


def _domain_name(registry: dict[str, Any]) -> str:
    return registry.get("domain", "当前域")


def build_schema_summary_prompt(question: str, context_text: str, registry: dict[str, Any]) -> str:
    domain_name = _domain_name(registry)
    return f"""你是 {domain_name} Text2SQL 链路中的 Schema Summary 节点。

你的任务不是写 SQL，而是把业务问题转成下游 SQL 生成需要的紧凑中文分析。

请严格输出以下小节：
【问题意图】
【推荐表】
【字段归属】
【业务词映射】
【JOIN 与分区】
【聚合与结果形态】
【风险点】

要求：
1. 只使用给定上下文里的表、字段、枚举、术语映射和指标口径。
2. 必须逐个识别用户问题里的业务概念，并在【字段归属】中写清楚：业务概念 -> 字段/指标 -> 完整表名。
3. 判断单表 / 多表时，以【字段归属】为准。只要所需字段、指标或维度分布在多张表，就必须推荐 JOIN。
4. 必须逐表核对上下文中的完整表名，不能改写库名、表名或字段名。
5. 【JOIN 与分区】必须说明：
   - 每张表如何补充分区过滤；
   - 如果需要 JOIN，优先使用上下文里给出的 join key、公共业务键或主键；
   - 如果上下文明确给了优先汇总表 / 明细表策略，也要写清楚选表依据。
6. 如果问题涉及比例、转化率、CTR、占比、均值、趋势、topN 或对比，必须明确结果粒度、分组维度和分母分子。
7. 如果字段或口径在给定上下文的其他表里存在，应推荐 JOIN，不要轻易输出“无法满足”。
8. 只有当所需字段或业务口径在所有给定上下文里都不存在时，才在【风险点】中明确说明“目前用户查询无法满足”。

用户问题：
{question}

{domain_name}上下文：
{context_text}
"""


def build_sql_prompt(question: str, context_text: str, schema_summary: str, registry: dict[str, Any]) -> str:
    domain_name = _domain_name(registry)
    default_metric = registry.get("global_rules", {}).get("default_metric", "")
    default_metric_rule = ""
    if default_metric:
        default_metric_rule = f"4. 默认指标规则：{default_metric}\n"
    return f"""你是 {domain_name} Text2SQL 链路中的 SQL 生成节点，请生成 ODPS / MaxCompute SQL。

必须遵守：
1. 只输出一个 SQL，放在 ```sql 代码块中，不要输出多个候选。
2. 只能使用给定上下文里出现的表、字段、术语映射和指标口径。
3. 所有物理表都必须补充分区过滤，并遵守上下文中的分区规则。
{default_metric_rule}5. 严格按照 Schema Summary 的【字段归属】写 SQL。字段或指标属于哪张表，就必须从那张表取；不允许迁移到其他表。
6. 如果所需字段分布在多张表，必须 JOIN。优先使用 Schema Summary 和上下文给出的 join key、主键或公共业务键。
7. 多表查询时，优先将每张物理表写成子查询，并在子查询中先做分区过滤，再 JOIN。
8. 比例、转化率、CTR、占比计算必须使用 NULLIF 避免除零。
9. 如果问题问趋势、对比、分布、topN、差异，结果字段要可解释，不能只输出一个黑盒标签。
10. 如果字段存在于给定上下文的其他表，必须通过 JOIN 使用，不允许直接输出“目前用户查询无法满足”。
11. 只有当所需字段或业务口径在所有给定上下文中都不存在时，才输出：
```sql
-- 目前用户查询无法满足：说明缺少的字段或口径
```

用户问题：
{question}

Schema Summary：
{schema_summary}

{domain_name}上下文：
{context_text}
"""


def build_selector_prompt(
    question: str,
    schema_summary: str,
    candidates: list[dict[str, Any]],
    registry: dict[str, Any],
) -> str:
    domain_name = _domain_name(registry)
    candidate_blocks = []
    for index, candidate in enumerate(candidates, start=1):
        validation = candidate["validation"]
        issues = "\n".join(
            f"- [{item['severity']}] {item['code']}：{item['message']} {item.get('evidence', '')}".strip()
            for item in validation["issues"]
        ) or "- 无静态校验问题"
        candidate_blocks.append(
            f"""## candidate_{index}
静态校验状态：{validation['status']}
错误数：{validation['error_count']}
警告数：{validation['warning_count']}

SQL：
```sql
{candidate['sql']}
```

校验问题：
{issues}
"""
        )

    return f"""你是 {domain_name} Text2SQL 链路中的最终 Selector。

你的任务是从候选 SQL 中选择最适合作为最终答案的一条。你不能生成新 SQL，不能改写候选 SQL，只能选择候选编号。

选择原则按优先级排序：
1. 先排除静态校验 status = fail 的候选，除非所有候选都是 fail。
2. 优先选择最符合用户问题语义、结果形态、业务口径和分组粒度的候选。
3. 如果候选输出“目前用户查询无法满足”，但 Schema Summary 或当前域上下文里其实存在相关字段，应强烈降权。
4. 如果候选把字段写到错误表，或把指标/维度挂到了不合理的明细层级，应强烈降权。
5. 多表 SQL 优先选择 join key 清晰、分区过滤完整、聚合层次合理的候选。
6. 检查表选择、字段选择、分区条件、JOIN 条件、聚合粒度、默认指标、比例分母是否合理。
7. 如果多个候选都可用，选择 SQL 更简单、更贴合问题的一条。
8. 如果所有候选都明显不可用，也必须选择相对问题最小的一条，并在理由中说明风险。

请严格输出：
[selected_candidate]
候选编号，例如 candidate_1

[reason]
中文选择理由，说明为什么选它，以及主要风险。

用户问题：
{question}

Schema Summary：
{schema_summary}

候选 SQL：
{chr(10).join(candidate_blocks)}
"""
