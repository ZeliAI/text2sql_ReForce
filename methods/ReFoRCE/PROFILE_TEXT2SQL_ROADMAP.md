# Text2SQL Agent Roadmap

本文档用于记录 Text2SQL agent 的迭代计划和状态。V1.0 是当前画像域单域 baseline；V1.1 开始进入线上化工程重构。后续每次完成一个迭代，都需要更新本文件。

## 状态说明

| 状态 | 含义 |
| --- | --- |
| Planned | 已计划，尚未执行 |
| In Progress | 正在进行 |
| Done | 已完成 |
| Blocked | 被依赖或问题阻塞 |

## 当前阶段

当前 V1.2 已启动：已接入投放域、push 域 markdown 到 registry 的自动构建能力，将 LLM 主题域解析接入线上 pipeline，并完成多域 context builder 与通用 prompt 接线。

V1.2 当前目标是在 V1.1 线上框架上接入画像域、投放域、push 域 registry，统一主题域解析和多域 context builder。当前 LLM router 已能基于多域 registry 将问题路由到画像域、投放域或 push 域；三域都已接入统一 context builder、schema summary prompt 和 SQL generation prompt。当前剩余重点转为调用稳定性与多域效果调优。

## Roadmap

| 阶段 | 状态 | 目标 | 交付物 |
| --- | --- | --- | --- |
| V1.0 画像域单域 baseline | Done | 建立可运行、可评测、可诊断的画像域 Text2SQL baseline。 | `profile_agent.py`、`profile_build_assets.py`、`profile_sql_validator.py`、`profile_baseline_report.py`、`data/profile_eval/` |
| V1.1 线上化工程重构 | Done | 隔离旧 Spider / ReFoRCE 榜单代码，新建线上 pipeline，支持节点级模型配置、路由、日期调整、安全兜底、mock online data 入口、长任务 timing / resume。 | `ONLINE_TEXT2SQL_REFACTOR_PLAN.md`、`online_agent/`、`online_profile_agent.py`、`configs/online_agent_v1_1.json`、`data/mock_warehouse/` |
| V1.2 多域知识与路由增强 | In Progress | 统一画像域、投放域、push 域 registry，支持 LLM 主题域解析、多域 context builder 和通用 SQL 生成链路。 | 多域 registry、LLM router、多域 context builder、多域评测样例 |
| V1.3 Mock Online Warehouse | Planned | 构造 mock 线上数据，接入可执行评测信号。 | `data/mock_warehouse/`、DuckDB / SQLite 执行器、expected result shape |
| V1.4 多轮与澄清 | Planned | 增加轻量澄清机制、memory 接口、多轮任务状态。 | clarifier、memory interface、多轮评测样例 |

## V1.0 详细记录

V1.0 由原 P0.0-P0.8 组成，以下保留历史细节，作为 baseline 追溯。

### P0.1 评测集结构化

输入：

- `data/文档二_画像域Text2SQL评测集.md`

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

- `data/画像域表合并/画像域_01_Schema总览.md`
- `data/画像域表合并/画像域_02_adm_asap_base_user_label_dd.md`
- `data/画像域表合并/画像域_03_adm_asap_algo_user_label_dd.md`
- `data/画像域表合并/画像域_04_adm_asap_pay_user_label_dd.md`
- `data/画像域表合并/画像域_05_adm_asap_other_action_user_label_dd.md`

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

当前状态：

1. `profile_build_assets.py` 已适配新路径，默认读取 `data/文档二_画像域Text2SQL评测集.md` 和 `data/画像域表合并/`。
2. `data/profile_eval/` 是自动生成资产，不是人工维护来源。
3. 当前 registry 重建结果为 30 条评测、4 张表、301 个字段、61 条业务术语映射、30 条指标口径、0 个未解析字段引用。

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

当前结果：

1. 已使用 simpleai Claude `claude-opus-4-6` 跑完 `output/profile-baseline-simpleai-30/`。
2. 旧 registry 下静态报告为 `pass 9 / fail 21`，候选总数 60。
3. 新 registry 补齐通用 `user_id` 后，对同一批 SQL 重新静态校验为 `pass 13 / warning 7 / fail 10`。
4. 失败类型集中在：空 SQL 输出、CTE / 派生表别名被误判、JOIN `dt` 静态识别不足、少量真实字段选择或字段归属风险。

### P0.8 错误归因与第一轮链路修正

动作：

1. 修复 `profile_agent.py` 对空 SQL / 非 SQL 输出的候选保护，避免最终 `result.sql` 为空。
2. 增强 `profile_sql_validator.py` 对 CTE、派生表、子查询别名、窗口函数和 ODPS 常用函数的解析。
3. 将静态校验报告区分为“校验器能力不足”和“真实 SQL 风险”。
4. 抽样人工对照 `expected_analysis`，优先分析 U011、U021、U024、U027、U028、U030 等空 SQL 或无表样本。
5. 再根据真实错误修 schema summary prompt 和 SQL generation prompt。

验收：

1. 对已跑出的 30 条 SQL 重新校验，静态误报明显下降。
2. 空 SQL 输出被识别并自动降级为候选失败，不再污染最终结果。
3. baseline 报告能输出更可信的错误分类。

## 当前约定

1. 调试模型统一使用 `claude-opus-4-6`。
2. 当前只做画像域，不做多域路由；投放域和 push 域文档已入库，作为后续多域迭代输入。
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
| 2026-05-07 | 数据路径调整 | 原始业务文档改为 `data/画像域表合并/`、`data/文档二_画像域Text2SQL评测集.md`；投放域和 push 域文档已补入 `data/投放域表合并/`、`data/push域表合并/`；`profile_build_assets.py` 已适配新路径。 |
| 2026-05-07 | P0.7 baseline | 使用 simpleai Claude `claude-opus-4-6` 跑完 30 条画像域 baseline，输出目录为 `output/profile-baseline-simpleai-30/`；旧 registry 静态结果 `pass 9 / fail 21`，当前 validator 重校验 `pass 13 / warning 7 / fail 10`。 |
| 2026-05-07 | P0.8 启动 | 发现主要问题为 CTE / 派生表别名校验误报、空 SQL 输出、JOIN `dt` 静态识别不足，以及少量真实字段选择风险；下一轮优先修 validator 和空输出保护。 |
| 2026-05-07 | P0.8 修正一 | `profile_agent.py` 增强非标准 SQL 代码块抽取和画像域字段提示召回；`profile_sql_validator.py` 增强空 SQL、CTE、派生表别名、注释剥离和 JOIN dt 静态识别；`profile_baseline_report.py` 新增 `--revalidate` 与错误归因分组。 |
| 2026-05-07 | P0.8 Prompt 修正 | 收紧 Schema Summary / SQL Generation / Selector prompt：字段必须逐项写归属表，多表必须 `user_id + dt` JOIN，字段存在于其他画像表时必须 JOIN，不允许误报无法满足；关键 10 题从旧输出重校验 `pass 13 / warning 7 / fail 10` 的问题集中样本，抽跑后达到 9 条 pass、1 条 warning，U021 二次修正后单跑 pass。 |
