from typing import Any


def build_domain_router_prompt(question: str, registries: list[dict[str, Any]]) -> str:
    domain_blocks = []
    for registry in registries:
        concepts = "、".join(item["concept"] for item in registry.get("concepts", [])[:12])
        terms = "、".join(item["term"] for item in registry.get("business_terms", [])[:20])
        rules = "；".join(
            f"{item['scenario']} -> {item['table']}"
            for item in registry.get("table_selection_rules", [])[:8]
        )
        domain_blocks.append(
            f"""## {registry['domain']}
域说明：{registry.get('domain_description', '')}
核心概念：{concepts or '无'}
高频术语：{terms or '无'}
选表规则：{rules or '无'}
"""
        )

    return f"""你是专业的 NL 数据主题域解析专家，需要根据用户问题和已注册知识库判断唯一主题域。

要求：
1. 仅输出一个结果：画像域、投放域、push域、策略域。
2. 唯一性原则：即使包含多个关键词，也选择最贴合核心语义目的的一个主题域。
3. 语义目的优先：描述、筛选或分析用户特征归画像域；评估或优化推送效果/配置归 push域；衡量广告/流量/商业化效果归投放域；业务策略和规则执行归策略域。
4. 上下文敏感："push点击率"归 push域；"经常点击push的用户"归画像域；"广告点击率"归投放域。
5. 不要解释，不要输出 JSON，不要多选。

已注册知识库：
{chr(10).join(domain_blocks)}

用户查询：
{question}

所属主题域：
"""
