# 画像域 Text2SQL Agent Roadmap

本文档用于记录画像域 Text2SQL agent 的迭代计划和状态。后续每次完成一个迭代，都需要更新本文件。

## 状态说明

| 状态 | 含义 |
| --- | --- |
| Planned | 已计划，尚未执行 |
| In Progress | 正在进行 |
| Done | 已完成 |
| Blocked | 被依赖或问题阻塞 |

## 当前阶段

当前处于 P0：画像域单域 baseline 搭建阶段。

目标是先在 30 条画像域评测集上建立可运行、可评测、可诊断的 Text2SQL agent baseline。

## Roadmap

| 阶段 | 状态 | 目标 | 交付物 |
| --- | --- | --- | --- |
| P0.0 文档整理 | Done | 拆分业务文档，删除旧 Spider2 / OmniSQL 优化文档，建立新 PRD 和 Roadmap。 | `data/业务评测集_markdown/`、`PROFILE_TEXT2SQL_PRD.md`、`PROFILE_TEXT2SQL_ROADMAP.md` |
| P0.1 评测集结构化 | Done | 将 `文档二_画像域Text2SQL评测集.md` 中 30 条题目解析成 JSON / JSONL，保留 id、难度、问题、预期分析。 | `data/profile_eval/profile_text2sql_eval.jsonl` |
| P0.2 知识文档转化 / Schema Registry 构建 | Done | 在线上只提供画像域 01-05 markdown 的前提下，在链路中自动抽取表、字段、类型、值域、业务词映射、指标口径，而不是要求业务同学重新整理知识文档。 | `data/profile_eval/profile_schema_registry.json`、`data/profile_eval/profile_schema_registry_build_log.md` |
| P0.3 中文 Schema Summary Prompt | In Progress | 设计画像域中文 schema summary prompt，输出相关表、字段、业务映射、JOIN、dt、风险点。 | `methods/ReFoRCE/profile_agent.py` 初版 |
| P0.4 中文 SQL Generation Prompt | In Progress | 设计画像域 ODPS SQL 生成 prompt，替换 Spider / OmniSQL 风格英文 prompt。 | `methods/ReFoRCE/profile_agent.py` 初版 |
| P0.5 静态 SQL 校验器 | Done | 在无真实数据情况下校验表字段、dt、JOIN、COUNT DISTINCT、枚举值、LIMIT 等规则。 | `methods/ReFoRCE/profile_sql_validator.py`、每条样本的 `validation.json` / `validation.md` |
| P0.6 多候选 Selector | Done | 生成多个候选 SQL，基于静态校验和业务语义选择最终 SQL。 | `profile_agent.py` 多候选参数、`selector.json` / `selector.md`、候选 SQL 校验日志 |
| P0.7 跑通 30 条 baseline | Planned | 使用 Claude `claude-opus-4-6` 跑 30 条画像域评测，输出 SQL、summary、校验结果、selector 结果。 | baseline 输出目录和评测报告 |
| P0.8 错误归因与第一轮 prompt 修正 | Planned | 统计错误类型，优先修正高频问题。 | 错误归因文档和 prompt 更新 |

## P0 详细计划

### P0.1 评测集结构化

输入：

- `data/业务评测集_markdown/文档二_画像域Text2SQL评测集.md`

动作：

1. 解析 U001-U030。
2. 提取问题、难度、A/B/C 分析、总分。
3. 输出 JSONL。

验收：

1. JSONL 共 30 条。
2. 每条包含 `id`、`difficulty`、`question`、`expected_analysis`。
3. 不把 expected analysis 注入 SQL 生成 prompt，只用于评测。

### P0.2 知识文档转化 / Schema Registry 构建

定位：

线上实际提供给链路的是画像域 01-05 的 markdown 文档。P0.2 不是要求业务同学额外整理结构化知识库，而是在 agent 链路里增加一个“知识文档转化节点”，把业务 markdown 自动转成机器可消费的 schema registry。

输入：

- `画像域_01_Schema总览.md`
- `画像域_02_adm_asap_base_user_label_dd.md`
- `画像域_03_adm_asap_algo_user_label_dd.md`
- `画像域_04_adm_asap_pay_user_label_dd.md`
- `画像域_05_adm_asap_other_action_user_label_dd.md`

动作：

1. 抽取 4 张表的完整路径、分区字段、字段列表。
2. 抽取业务词映射和指标口径。
3. 抽取 JOIN 规则、dt 规则、常见 SQL 示例。
4. 保留转化日志，记录每个字段/映射来自哪个 markdown 文件和章节，便于业务同学追溯和修正文档。

验收：

1. 能通过字段名查到所属表。
2. 能通过业务词查到推荐 SQL 条件。
3. 能生成用于 prompt 的 compact schema context。
4. 输入仍然是业务 markdown；业务同学只维护 markdown，不需要手工维护 JSON registry。

### P0.3 / P0.4 Prompt 中文化

动作：

1. 新增画像域 schema summary prompt。
2. 新增画像域 SQL generation prompt。
3. 明确“无法满足”输出。
4. 明确 ODPS SQL 格式。

验收：

1. prompt 全中文。
2. 业务同学能直接读懂并修改。
3. 对 U001-U010 简单题能稳定生成合理 SQL。

### P0.5 静态 SQL 校验

动作：

1. 解析 SQL 中的表名和字段。
2. 校验字段归属。
3. 校验 dt 分区。
4. 校验 JOIN key。
5. 校验常见业务口径。

验收：

1. 能识别伪造字段。
2. 能识别漏 dt。
3. 能识别多表 JOIN 漏 `dt` 或 `user_id`。
4. 能输出中文校验报告，供 self-refine / selector 使用。

### P0.6 Selector

动作：

1. 多候选生成。
2. 对每个候选运行静态校验。
3. 用中文 selector 选择最终 SQL。

验收：

1. selector 不生成新 SQL，只选择候选。
2. selector 日志包含候选 SQL、校验结果和选择理由。

### P0.7 Baseline

动作：

1. 跑 30 条画像域评测。
2. 保存每条的 schema summary、候选 SQL、校验结果、最终 SQL。
3. 输出汇总报告。

验收：

1. 30 条均有最终输出。
2. 每条都有可追踪日志。
3. 能按错误类型汇总。

## 当前约定

1. 调试模型统一使用 `claude-opus-4-6`。
2. 当前只做画像域，不做多域路由。
3. 当前没有真实数据，短期不以执行结果作为主评测依据。
4. prompt 使用中文，便于业务同学后续维护。
5. 后续每次完成迭代，都要更新本 Roadmap 的状态和备注。

## 迭代记录

| 日期 | 迭代 | 更新内容 |
| --- | --- | --- |
| 2026-05-07 | P0.0 | 拆分业务 markdown，删除旧 Spider2 / OmniSQL 优化路线文档，新增 PRD 和 Roadmap。 |
| 2026-05-07 | P0.1 / P0.2 | 新增 `profile_build_assets.py`，从业务 markdown 生成 30 条评测 JSONL、画像域 schema registry、compact context 和转化日志；registry 合并 01 总览核心字段与 02-05 表明细，当前字段引用检查为 0 个未解析。 |
| 2026-05-07 | P0.3 / P0.4 初版 | 新增 `profile_agent.py`，实现中文 Schema Summary prompt 与中文 ODPS SQL Generation prompt，并用 `claude-opus-4-6` 跑通 U001 smoke。 |
| 2026-05-07 | P0.5 | 新增 `profile_sql_validator.py`，支持表/字段归属、dt 分区、多表 JOIN key、COUNT DISTINCT、topN LIMIT、无法满足输出等静态校验；已接入 `profile_agent.py`，每条样本自动输出校验 JSON 和中文报告。 |
| 2026-05-07 | P0.6 | `profile_agent.py` 新增 `--num-candidates` 和 `--use-selector`，支持多候选 SQL 生成、候选级静态校验、中文 selector 只选不改写；U001 已跑通 3 候选 + selector。 |
