# Online Text2SQL Refactor Plan

本文档从 V1.1 开始规划线上化重构。V1.0 指当前已经跑通的画像域单域 baseline，不再继续按 P0 / V0.x 命名。

## 版本定义

| 版本 | 状态 | 目标 |
| --- | --- | --- |
| V1.0 | Done | 画像域单域 baseline：业务 markdown -> registry -> compact context -> schema summary -> 多候选 SQL -> 静态校验 -> selector -> report。 |
| V1.1 | Done | 线上化工程重构：旧 Spider / ReFoRCE 榜单代码隔离，新建线上 agent pipeline，支持节点级模型配置、路由、日期调整、安全兜底和 mock online data 入口。 |
| V1.2 | In Progress | 多域知识与路由增强：画像域、投放域、push 域统一 registry，支持单域 / 混合域识别和多域 context builder。 |
| V1.3 | Planned | Mock Online Warehouse：构造 mock 线上数据，接入可执行评测信号。 |
| V1.4 | Planned | 多轮与澄清：轻量澄清机制、memory 接口、多轮任务状态。 |

## V1.0 基线

当前 V1.0 已具备：

1. 画像域 30 条评测集。
2. 画像域 schema registry、compact context、构建日志。
3. 中文 Schema Summary prompt。
4. 中文 ODPS SQL Generation prompt。
5. 多候选生成与 LLM selector。
6. 静态 SQL validator，覆盖表字段、dt、JOIN、COUNT DISTINCT、LIMIT、无法满足等规则。
7. baseline report 和 revalidate report。
8. simpleai Claude `claude-opus-4-6` 调试链路。

V1.0 的主要价值是证明画像域单域链路可运行、可诊断、可迭代。V1.1 起不再继续在旧单脚本上堆功能，而是把能力迁移到线上化框架。

## V1.1 目标架构

当前线上 agent 已经从 `methods/ReFoRCE` 目录上提到仓库根目录。团队测试默认使用 `online_agent/`、`run_online_agent.py`、`build_domain_registry.py` 和 `configs/online_agent_v1_2.json`；`methods/ReFoRCE` 下仅保留兼容 wrapper 和历史代码。

当前已经采用独立线上目录，避免继续受 Spider / ReFoRCE 榜单代码影响。

```text
online_agent/
configs/
docs/
run_online_agent.py
build_domain_registry.py
data/
```

## Pipeline

V1.1 线上链路目标：

```text
用户问题 + 可选多轮上下文
-> router
-> clarifier / reject / continue
-> date_adjuster
-> registry_loader
-> context_builder
-> schema_summary
-> sql_generator
-> static_validator
-> safety_guard
-> selector
-> final SQL / 无法满足 / 反问
```

节点说明：

| 节点 | 说明 | V1.1 优先级 |
| --- | --- | --- |
| router | 判断单域 / 混合域，以及涉及画像域、投放域、push 域等哪些域。 | 高 |
| clarifier | 面对无法执行或信息不足的问题，做拒答或基础反问。 | 中 |
| date_adjuster | 保留线上日期调整环节，放在多候选 SQL 生成之前。 | 高 |
| registry_loader | 读取统一 registry，而不是从 prompt 硬编码业务词。 | 高 |
| context_builder | 构造 ReFoRCE 风格 compact context。 | 高 |
| schema_summary | 压缩用户问题、字段归属、表选择、JOIN、dt、风险点。 | 高 |
| sql_generator | 大模型多候选 SQL 生成。 | 高 |
| static_validator | 规则校验表字段、分区、JOIN、LIMIT、聚合口径等。 | 高 |
| safety_guard | 无法满足、安全限制、权限、分区、LIMIT、DDL/DML 禁止。 | 高 |
| selector | 大模型基于候选 SQL、校验和可选 mock 执行结果选择最终答案。 | 高 |
| memory | 多轮上下文和任务状态。 | 低 |

## 节点级模型配置

每个 LLM 节点都必须独立可配置。前期调试默认大模型 Claude、小模型 Moonshot `moonshot-v1-128k`，但代码不能把这种分工写死。

示例配置：

```yaml
llm:
  nodes:
    router:
      provider: moonshot
      model: moonshot-v1-128k
      temperature: 0.2
    clarifier:
      provider: moonshot
      model: moonshot-v1-128k
      temperature: 0.2
    date_adjuster:
      provider: moonshot
      model: moonshot-v1-128k
      temperature: 0.1
    schema_summary:
      provider: moonshot
      model: moonshot-v1-128k
      temperature: 0.2
    sql_generation:
      provider: simpleai
      model: claude-opus-4-6
      temperature: 0.6
      num_candidates: 2
    llm_validator:
      provider: moonshot
      model: moonshot-v1-128k
      temperature: 0.1
    selector:
      provider: simpleai
      model: claude-opus-4-6
      temperature: 0.2
```

代码侧使用节点名取模型：

```python
llm_for("router")
llm_for("schema_summary")
llm_for("sql_generation")
llm_for("selector")
```

后续如果单独训练某个节点模型，只改配置，不改 pipeline。

## Registry 与业务知识沉淀

V1.1 要把高频业务词、指标口径、字段别名、枚举值、JOIN 规则、分区规则沉淀到 registry，不继续散落在 prompt。

建议统一数据目录：

```text
data/business_docs/
  profile/
  marketing/
  push/

data/eval_sets/
  profile/
  marketing/
  push/

data/registries/
  profile_registry.json
  marketing_registry.json
  push_registry.json

data/context_assets/
  profile_compact_context.md
  marketing_compact_context.md
  push_compact_context.md
```

V1.1 可以先迁移画像域；V1.2 再扩展投放域和 push 域。

## Mock Online Data

V1.1 需要预留 mock online data 入口；V1.3 正式建设 mock execution。

建议目录：

```text
data/mock_warehouse/
  profile/
    adm_asap_base_user_label_dd.csv
    adm_asap_algo_user_label_dd.csv
    adm_asap_pay_user_label_dd.csv
    adm_asap_other_action_user_label_dd.csv
  marketing/
  push/
```

mock 数据目标：

1. 验证 SQL 语法和结果形态。
2. 验证 `user_id + dt` JOIN。
3. 验证分区过滤、LIMIT、聚合和比例。
4. 构造典型枚举值和边界值。
5. 为 selector 提供可选执行结果信号。

执行器可以先使用 DuckDB / SQLite，不追求完整 ODPS 兼容。

## Safety Guard

线上兜底必须保留并前置设计：

1. 无法满足：字段、表、口径、权限缺失。
2. 安全限制：禁止 DDL / DML，如 `INSERT`、`UPDATE`、`DELETE`、`DROP`。
3. LIMIT：明细查询必须限制行数。
4. 分区：分区表必须过滤 `dt` / `hh` 等分区字段。
5. 权限：域级、表级、字段级权限校验。
6. 成本保护：无分区、多大表 JOIN、全表扫描风险。
7. SQL 方言：ODPS / MaxCompute 语法约束。

## V1.1 交付物

1. Done：新线上目录已经统一到仓库根目录 `online_agent/`。
2. Done：旧 Spider / ReFoRCE 榜单代码隔离说明 `LEGACY_SPIDER_README.md`、`methods/legacy_reforce/README.md`。
3. Done：pipeline 节点接口，包括 router、clarifier、date_adjuster、registry_loader、context_builder、schema_summary、sql_generator、validator、safety_guard、selector。
4. Done：节点级 LLM config `configs/online_agent_v1_1.json`。
5. Done：V1.0 画像域能力迁移到新框架，可通过 `run_online_agent.py` 跑线上样本。
6. Done：router 初版。多域精细路由留到 V1.2 结合投放域 / push 域 registry 一起处理。
7. Done：date_adjuster 初版，位于 SQL generation 前。
8. Done：safety_guard 初版，覆盖 DDL / DML 禁止、分区和明细 LIMIT 基础兜底。
9. Done：mock online data 目录和 profile mock CSV 入口。
10. Done：长任务 timing、增量日志、resume 能力。
11. Done：基础字段幻觉保护 `schema_summary_guard`。

V1.1 收口说明：本版本只做线上化骨架和基础安全保障，不做重型字段归属解析；复杂业务语义优先通过模型能力和知识库质量解决。多域 registry、主题域解析增强和跨域上下文构造进入 V1.2。

## V1.2 当前进展

1. Done：投放域、push 域 markdown 自动构建 registry，输出到 `data/domain_registries/`。
2. Done：参考 `data/text2sql线上链路.md` 的“主题域解析（LLM）”思路，接入 LLM router 作为默认主题域解析节点。
3. Done：LLM router 输出统一映射到 `profile`、`marketing`、`push`、`strategy`；无效输出或调用失败时回退规则 router。
4. Done：多域 context builder 接入线上 pipeline，按 registry 自动组织域说明、全局规则、选表规则、相关表字段、术语映射、指标口径和参考 SQL。
5. Done：通用 schema summary / SQL generation / selector prompt 接入，投放域、push 域不再复用画像域专属 prompt。
6. Done：静态 validator 放宽为多域通用版本，不再强依赖画像域 `user_id + dt` JOIN 规则。
7. Done：CLI 增加节点异常兜底，遇到上游 `SystemExit` / 连接错误时仍然落完整 run artifacts。
8. Next：处理上游 API 连续调用稳定性，补充节点级重试与更细粒度错误归因。
