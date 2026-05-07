import argparse
import json
import re
from pathlib import Path
from typing import Any

from chat import GPTChat
from profile_sql_validator import render_validation_markdown, validate_sql


REPO_ROOT = Path(__file__).resolve().parents[2]
DEFAULT_ASSET_DIR = REPO_ROOT / "data" / "profile_eval"


QUESTION_FIELD_HINTS = [
    ("沉默期", ["life_cycle"]),
    ("衰退期", ["life_cycle"]),
    ("成长期", ["life_cycle"]),
    ("新手期", ["life_cycle"]),
    ("生命周期", ["life_cycle"]),
    ("回流潜力", ["reactivation_level"]),
    ("提频潜力", ["freq_uplift_level"]),
    ("沉默风险", ["silence_risk_level"]),
    ("积分偏好", ["pts_prefer_level"]),
    ("红包偏好", ["rp_prefer_level"]),
    ("权益偏好", ["pts_prefer_level", "ec_prefer_level", "mev_prefer_level", "rp_prefer_level", "if_prefer_level", "faid_prefer_level"]),
    ("eM+高营销敏感", ["em_marketing_sensitivity"]),
    ("营销敏感", ["em_marketing_sensitivity"]),
    ("eM+高潜", ["em_potential_segment"]),
    ("基金高潜", ["fund_potential_segment"]),
    ("年龄", ["user_age", "user_age_group"]),
    ("性别", ["user_gender"]),
    ("男女", ["user_gender"]),
    ("支付高频", ["trx_freq_level_r30d", "pay_level_r30d"]),
    ("高频高金额", ["trx_freq_level_r30d", "trx_amt_level_r30d", "pay_level_r30d"]),
    ("高金额", ["trx_amt_level_r30d", "pay_level_r30d"]),
    ("交易笔数", ["transact_num_r30d", "transact_num_r7d"]),
    ("交易次数", ["transact_num_r30d", "transact_num_r7d"]),
    ("交易金额", ["transact_amt_r30d", "transact_amt_r7d"]),
    ("充值金额", ["topup_amt_r30d", "topup_amt_r7d"]),
    ("充值笔数", ["topup_cnt_r30d", "topup_cnt_r7d"]),
    ("登录频率", ["login_cnt_r30d", "user_login_frequency"]),
    ("登录次数", ["login_cnt_r30d", "login_cnt_r7d"]),
    ("push高频", ["user_push_activity_level", "push_click_cnt_r30d", "user_push_cilck_pv_r30d"]),
    ("push点击", ["user_push_cilck_pv_r30d", "push_click_cnt_r30d", "is_push_click_user"]),
    ("push触达", ["user_push_exposure_pv_r30d"]),
    ("领券", ["send_cnt_r30d"]),
    ("核销", ["use_cnt_r30d"]),
    ("绑卡", ["effective_bind_card_cnt", "bind_card_cnt"]),
]


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


def compact_text(value: str, limit: int = 260) -> str:
    value = re.sub(r"\s+", " ", value).strip()
    return value if len(value) <= limit else value[: limit - 3] + "..."


def score_table(question: str, table: dict[str, Any], business_terms: list[dict[str, str]]) -> int:
    score = 0
    table_name = table["table_name"]
    if table_name in question or table_name.replace("adm_asap_", "").replace("_user_label_dd", "") in question:
        score += 4
    for column in table["columns"]:
        if column["name"] in question:
            score += 3
        cn_name = column.get("cn_name") or ""
        if cn_name and any(piece and piece in question for piece in re.split(r"[/（）()、,， ]+", cn_name)):
            score += 1
    table_fields = {column["name"] for column in table["columns"]}
    for term in business_terms:
        normalized_term = term["term"].replace("用户", "").replace("（", "").replace("）", "")
        term_pieces = [piece for piece in re.split(r"[/（）()、,， ]+", term["term"]) if piece]
        if (
            term["term"] in question
            or (normalized_term and normalized_term in question)
            or any(piece in question for piece in term_pieces)
        ):
            refs = set(re.findall(r"\b[a-zA-Z_][a-zA-Z0-9_]*\b", term["sql"]))
            if refs & table_fields:
                score += 5
    for phrase, fields in QUESTION_FIELD_HINTS:
        if phrase in question and set(fields) & table_fields:
            score += 6
    return score


def select_context(question: str, registry: dict[str, Any], max_columns_per_table: int = 140) -> dict[str, Any]:
    terms = [
        term
        for term in registry["business_terms"]
        if term["term"] in question
        or term["term"].replace("用户", "") in question
        or any(piece and piece in question for piece in re.split(r"[/（）()、,， ]+", term["term"]))
    ]
    table_scores = [(score_table(question, table, registry["business_terms"]), table) for table in registry["tables"]]
    selected_tables = [table for score, table in sorted(table_scores, key=lambda item: item[0], reverse=True) if score > 0]
    selected_names = {table["full_name"] for table in selected_tables}
    for phrase, fields in QUESTION_FIELD_HINTS:
        if phrase not in question:
            continue
        for field in fields:
            for full_name in registry.get("field_index", {}).get(field, []):
                if full_name in selected_names:
                    continue
                table = next((item for item in registry["tables"] if item["full_name"] == full_name), None)
                if table:
                    selected_tables.append(table)
                    selected_names.add(full_name)
    if not selected_tables:
        selected_tables = registry["tables"]

    context_tables = []
    for table in selected_tables:
        context_tables.append(
            {
                "full_name": table["full_name"],
                "table_name": table["table_name"],
                "description": compact_text(table["description"]),
                "columns": [
                    {
                        "name": column["name"],
                        "cn_name": column.get("cn_name", ""),
                        "type": column.get("type", ""),
                        "description": compact_text(column.get("description", ""), 120),
                    }
                    for column in table["columns"][:max_columns_per_table]
                ],
            }
        )

    return {
        "global_rules": registry["global_rules"],
        "tables": context_tables,
        "business_terms": terms[:20] if terms else registry["business_terms"][:30],
        "metrics": registry["metrics"],
    }


def render_context(context: dict[str, Any]) -> str:
    lines = [
        "【全局规则】",
        f"- JOIN：{context['global_rules']['join_rule']}",
        f"- dt：{context['global_rules']['dt_rule']}",
        f"- 默认指标：{context['global_rules']['default_metric']}",
        "",
        "【相关表和字段】",
    ]
    for table in context["tables"]:
        lines.append(f"- {table['full_name']}：{table['description']}")
        for column in table["columns"]:
            cn_name = f" / {column['cn_name']}" if column["cn_name"] else ""
            col_type = f" / {column['type']}" if column["type"] else ""
            desc = f" / {column['description']}" if column["description"] else ""
            lines.append(f"  - {column['name']}{cn_name}{col_type}{desc}")
    lines.extend(["", "【业务术语映射】"])
    for term in context["business_terms"]:
        lines.append(f"- {term['term']} -> {term['sql']}")
    lines.extend(["", "【指标口径】"])
    for metric in context["metrics"]:
        desc = f"；{metric['description']}" if metric.get("description") else ""
        lines.append(f"- {metric['name']}：{metric['expression']}{desc}")
    return "\n".join(lines)


def build_schema_summary_prompt(question: str, context_text: str) -> str:
    return f"""你是画像域 Text2SQL 链路中的 Schema Summary 节点。

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
1. 只使用给定画像域上下文里的表、字段、枚举和口径。
2. 必须逐个识别用户问题里的业务概念，并在【字段归属】中写清楚：业务概念 -> 字段 -> 完整表名。
3. 判断单表 / 多表时，以【字段归属】为准。只要所需字段分布在多张表，就必须推荐 JOIN；不能因为某张表命中多个业务词就误判为单表。
4. 不允许把字段迁移到错误表。例如 `life_cycle` 只在 base 表，`reactivation_level` 只在 algo 表，`transact_num_r30d` 只在 pay 表，`login_cnt_r30d` 只在 other_action 表。
5. 必须逐表核对上下文中的完整表名，不能改写库名。特别注意：
   - base 表是 `antsg_asap.adm_asap_base_user_label_dd`
   - algo 表是 `anthk_sg.adm_asap_algo_user_label_dd`
   - pay 表是 `antsg_asap.adm_asap_pay_user_label_dd`
   - other_action 表是 `antsg_asap.adm_asap_other_action_user_label_dd`
6. 年龄、性别、生命周期、港漂、注册来源等基础属性来自 base 表；交易金额、交易笔数、支付高频/高金额等交易标签来自 pay 表；偏好、潜客、沉默风险、回流潜力来自 algo 表；登录、push、领券、核销来自 other_action 表。
7. 所有表都必须考虑 dt 分区。多表时必须说明每张表先过滤 `dt = max_pt('完整表名')`，再用 `user_id + dt` JOIN。
8. 如果字段存在于其他画像域表，应推荐 JOIN，不要输出“无法满足”。
9. 只有当所需字段或业务口径在所有给定画像域上下文中都不存在时，才在【风险点】中明确说明“目前用户查询无法满足”。

用户问题：
{question}

画像域上下文：
{context_text}
"""


def build_sql_prompt(question: str, context_text: str, schema_summary: str) -> str:
    return f"""你是画像域 Text2SQL 链路中的 SQL 生成节点，请生成 ODPS / MaxCompute SQL。

必须遵守：
1. 只输出一个 SQL，放在 ```sql 代码块中，不要输出多个候选。
2. 只能使用画像域上下文里出现的表和字段。
3. 所有表必须加 dt 分区过滤。当前 P0 默认写法为：dt = max_pt('完整表名')。
4. 用户数默认使用 COUNT(DISTINCT user_id)。
5. 严格按照 Schema Summary 的【字段归属】写 SQL。字段在哪张表，就必须从那张表取；不允许把字段写到其他表。
6. 如果所需字段分布在多张表，必须 JOIN。JOIN 模板必须满足：
   - 每张物理表写成子查询。
   - 每个子查询都必须 SELECT `user_id`、`dt` 和本表需要的业务字段。
   - 每个子查询都必须在 WHERE 中过滤 `dt = max_pt('完整表名')`。
   - JOIN 条件必须包含 `a.user_id = b.user_id AND a.dt = b.dt`；三表 JOIN 也必须逐段包含 user_id 和 dt。
7. 单表查询时也必须写 `dt = max_pt('完整表名')`。
8. 比例计算必须使用 NULLIF 避免除零。
9. 如果问题问“水平”“差异”“对比”，优先输出可解释的 AVG / SUM / COUNT / ratio 指标，不要只输出一个无法解释的标签。
10. 如果字段存在于画像域上下文的其他表，必须通过 JOIN 使用，不允许输出“目前用户查询无法满足”。
11. 只有当所需字段或业务口径在所有给定画像域上下文中都不存在时，才输出：
```sql
-- 目前用户查询无法满足：说明缺少的字段或口径
```

用户问题：
{question}

Schema Summary：
{schema_summary}

画像域上下文：
{context_text}
"""


def build_selector_prompt(question: str, schema_summary: str, candidates: list[dict[str, Any]]) -> str:
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
    return f"""你是画像域 Text2SQL 链路中的最终 Selector。

你的任务是从候选 SQL 中选择最适合作为最终答案的一条。你不能生成新 SQL，不能改写候选 SQL，只能选择候选编号。

选择原则按优先级排序：
1. 先排除静态校验 status = fail 的候选，除非所有候选都是 fail。
2. 优先选择最符合用户问题语义、结果形态和业务口径的候选。
3. 如果候选输出“目前用户查询无法满足”，但 Schema Summary 或画像域上下文里其实存在相关字段，应强烈降权。
4. 如果候选把字段写到错误表，应强烈降权，即使 SQL 看起来更短。
5. 多表 SQL 必须优先选择显式 `user_id + dt` JOIN 的候选；只有当所有物理表都已 `max_pt` 过滤且没有更好候选时，才接受只有 `user_id` JOIN 的候选，并在理由中说明风险。
6. 检查表选择、字段选择、dt 分区、JOIN key、聚合粒度、COUNT DISTINCT、比例分母是否合理。
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


def generate_candidate(chat: GPTChat, sql_prompt: str, registry: dict[str, Any], question: str) -> dict[str, Any]:
    raw_sql_response = chat.get_model_response_txt(sql_prompt).strip()
    sql = extract_sql(raw_sql_response)
    validation = validate_sql(sql, registry, question)
    return {
        "sql": sql,
        "validation": validation,
        "raw_sql_response": raw_sql_response,
    }


def run_one(chat: GPTChat, record: dict[str, Any], registry: dict[str, Any], num_candidates: int = 1, use_selector: bool = False) -> dict[str, Any]:
    question = record["question"]
    context = select_context(question, registry)
    context_text = render_context(context)
    summary_prompt = build_schema_summary_prompt(question, context_text)
    schema_summary = chat.get_model_response_txt(summary_prompt).strip()
    sql_prompt = build_sql_prompt(question, context_text, schema_summary)
    candidates = []
    for _ in range(max(1, num_candidates)):
        candidates.append(generate_candidate(chat, sql_prompt, registry, question))

    selected_index = 0
    selector_response = ""
    selector_reason = ""
    if use_selector and len(candidates) > 1:
        selector_prompt = build_selector_prompt(question, schema_summary, candidates)
        selector_response = chat.get_model_response_txt(selector_prompt).strip()
        selected = extract_selected_candidate(selector_response, len(candidates))
        selected_index = selected - 1 if selected else select_by_validation(candidates)
        reason_match = re.search(r"\[reason\]\s*(.*)", selector_response, flags=re.IGNORECASE | re.DOTALL)
        selector_reason = reason_match.group(1).strip() if reason_match else selector_response
    else:
        selected_index = select_by_validation(candidates)

    static_best_index = select_by_validation(candidates)
    selected_status = candidates[selected_index]["validation"]["status"]
    static_best_status = candidates[static_best_index]["validation"]["status"]
    if selected_status == "fail" and static_best_status != "fail":
        selector_reason = (
            (selector_reason + "\n\n" if selector_reason else "")
            + f"系统保护：LLM selector 选择了 candidate_{selected_index + 1}，但该候选静态校验为 fail；"
            + f"已自动回退到静态校验更优的 candidate_{static_best_index + 1}。"
        )
        selected_index = static_best_index

    selected_candidate = candidates[selected_index]
    return {
        "id": record["id"],
        "difficulty": record["difficulty"],
        "question": question,
        "schema_summary": schema_summary,
        "sql": selected_candidate["sql"],
        "validation": selected_candidate["validation"],
        "raw_sql_response": selected_candidate["raw_sql_response"],
        "candidates": candidates,
        "selected_candidate": f"candidate_{selected_index + 1}",
        "selector_response": selector_response,
        "selector_reason": selector_reason,
        "context_tables": [table["full_name"] for table in context["tables"]],
    }


def main() -> None:
    parser = argparse.ArgumentParser(description="Run profile-domain Text2SQL P0 chain.")
    parser.add_argument("--asset-dir", type=Path, default=DEFAULT_ASSET_DIR)
    parser.add_argument("--output-dir", type=Path, default=Path("output/profile-p0-smoke"))
    parser.add_argument("--limit", type=int, default=1)
    parser.add_argument("--offset", type=int, default=0)
    parser.add_argument("--sample-ids", default="", help="Comma-separated ids such as U001,U004. Overrides limit/offset.")
    parser.add_argument("--model", default="")
    parser.add_argument("--temperature", type=float, default=0.6)
    parser.add_argument("--num-candidates", type=int, default=1)
    parser.add_argument("--use-selector", action="store_true")
    args = parser.parse_args()

    eval_records = load_jsonl(args.asset_dir / "profile_text2sql_eval.jsonl")
    registry = json.loads((args.asset_dir / "profile_schema_registry.json").read_text(encoding="utf-8"))
    if args.sample_ids:
        wanted = {item.strip() for item in args.sample_ids.split(",") if item.strip()}
        records = [record for record in eval_records if record["id"] in wanted]
    else:
        records = eval_records[args.offset : args.offset + args.limit]

    model = args.model or __import__("os").environ.get("LLM_MODEL", "claude-opus-4-6")
    chat = GPTChat(model=model, temperature=args.temperature)
    args.output_dir.mkdir(parents=True, exist_ok=True)

    outputs = []
    for record in records:
        chat.init_messages()
        item = run_one(chat, record, registry, num_candidates=args.num_candidates, use_selector=args.use_selector)
        outputs.append(item)
        sample_dir = args.output_dir / item["id"]
        sample_dir.mkdir(parents=True, exist_ok=True)
        (sample_dir / "schema_summary.md").write_text(item["schema_summary"] + "\n", encoding="utf-8")
        (sample_dir / "result.sql").write_text(item["sql"] + "\n", encoding="utf-8")
        (sample_dir / "validation.json").write_text(json.dumps(item["validation"], ensure_ascii=False, indent=2), encoding="utf-8")
        (sample_dir / "validation.md").write_text(render_validation_markdown(item["validation"]), encoding="utf-8")
        for index, candidate in enumerate(item["candidates"], start=1):
            candidate_dir = sample_dir / f"candidate_{index}"
            candidate_dir.mkdir(exist_ok=True)
            (candidate_dir / "result.sql").write_text(candidate["sql"] + "\n", encoding="utf-8")
            (candidate_dir / "validation.json").write_text(json.dumps(candidate["validation"], ensure_ascii=False, indent=2), encoding="utf-8")
            (candidate_dir / "validation.md").write_text(render_validation_markdown(candidate["validation"]), encoding="utf-8")
            (candidate_dir / "raw_response.md").write_text(candidate["raw_sql_response"] + "\n", encoding="utf-8")
        selector_log = {
            "selected_candidate": item["selected_candidate"],
            "selector_response": item["selector_response"],
            "selector_reason": item["selector_reason"],
        }
        (sample_dir / "selector.json").write_text(json.dumps(selector_log, ensure_ascii=False, indent=2), encoding="utf-8")
        (sample_dir / "selector.md").write_text(
            f"# Selector 结果\n\n- 选择：{item['selected_candidate']}\n\n## 理由\n\n{item['selector_reason'] or '未启用 LLM selector，按静态校验排序选择。'}\n",
            encoding="utf-8",
        )
        (sample_dir / "log.json").write_text(json.dumps(item, ensure_ascii=False, indent=2), encoding="utf-8")
        print(f"{item['id']} -> {sample_dir / 'result.sql'} [{item['validation']['status']}, {item['selected_candidate']}]")

    (args.output_dir / "run.json").write_text(json.dumps(outputs, ensure_ascii=False, indent=2), encoding="utf-8")


if __name__ == "__main__":
    main()
