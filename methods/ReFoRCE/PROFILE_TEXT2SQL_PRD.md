# 画像域 Text2SQL Agent PRD

## 1. 背景

当前项目最初基于 ReFoRCE Text2SQL 框架做本地调试。现在目标切换为：在一个用户画像业务评测集上，对现有 Text2SQL 链路进行适配和优化。

线上业务数据分为多个主题域，包括画像域、投放域、push 域、策略域等。线上链路通常先识别用户问题所属主题域，再召回该主题域的知识库和表结构，随后完成意图解析、字段映射、SQL 生成和 SQL 校验。

为降低调试复杂度，当前阶段只聚焦画像域。画像域由 4 张 ADM 用户画像表组成，评测集包含 30 条自然语言查询，覆盖简单、中等、困难三档。

## 2. 当前任务目标

短期目标不是继续优化 Spider2 / OmniSQL 数据集，而是构建一条可在画像域业务评测集上迭代的 Text2SQL agent 链路。

当前需要做到：

1. 读取画像域评测集和画像域 schema 文档。
2. 基于画像域业务知识生成 ODPS / MaxCompute SQL。
3. 重点提升业务语义映射正确性，包括表选择、字段选择、枚举值映射、指标口径、JOIN 方式和分区规则。
4. 在没有真实数据的情况下，先通过静态 SQL 校验和 LLM selector 评估 SQL 质量。
5. 保留 ReFoRCE P0 的短期思想：生成前 schema / 业务上下文压缩，生成后候选 SQL 选择与校验。

## 3. 现有文档

画像域业务文档由 `data/合并表结构.txt` 拆分得到，拆分脚本为：

- `data/split_md.py`

拆分后的 markdown 目录：

- `data/业务评测集_markdown/`

核心文档如下：

| 文档 | 作用 |
| --- | --- |
| `text2sql线上链路.md` | 介绍当前线上 Text2SQL 链路，包括语义判断、主题域解析、意图解析、意图替换、日期调整、SQL 生成、SQL 校验等节点，以及线上 prompt 示例。 |
| `文档二_画像域Text2SQL评测集.md` | 画像域 30 条评测集，包含难度、问题、语义映射分析、选表分析、SQL 复杂度分析。 |
| `画像域_01_Schema总览.md` | 画像域整体说明，包含 4 张表清单、表关联关系、选表规则、指标口径、业务术语映射、核心字段速查、SQL 示例和注意事项。 |
| `画像域_02_adm_asap_base_user_label_dd.md` | 用户基础画像表明细，覆盖用户状态、年龄、性别、港漂、认证、设备、LBS、生命周期、价值、风控等字段。 |
| `画像域_03_adm_asap_algo_user_label_dd.md` | 用户行为偏好表明细，覆盖权益偏好、业务偏好、eM+ 潜客、基金潜客、回流潜力、沉默风险等字段。 |
| `画像域_04_adm_asap_pay_user_label_dd.md` | 用户交易行为表明细，覆盖交易金额、交易笔数、绑卡、充值、交易场景、出行、理财等字段。 |
| `画像域_05_adm_asap_other_action_user_label_dd.md` | 用户非交易行为表明细，覆盖登录、活跃、领券、核销、push 互动、页面点击、商户关注等字段。 |

文档中的语雀链接暂时忽略，不作为当前 agent 输入来源。

线上实际任务提供的知识输入就是上述画像域 markdown 文档，尤其是 `画像域_01_Schema总览.md` 到 `画像域_05_adm_asap_other_action_user_label_dd.md`。因此，结构化 schema registry 是系统链路里的自动转化产物，不要求业务同学额外维护一份 JSON 或数据库形式的知识库。

## 4. 线上链路理解

当前线上链路大致为：

```mermaid
flowchart TD
    A["用户自然语言查询"] --> B["语义判断<br/>单表 / 多表"]
    B --> C["主题域解析<br/>投放域 / 画像域 / push域 / 策略域"]
    C --> D["主题域知识召回<br/>按域注入对应 schema / 知识库"]
    D --> E["意图解析<br/>metrics / dimensions / filters / time_range"]
    E --> F["意图替换<br/>业务词映射到表 / 字段 / 枚举 / 口径"]
    F --> G["替换校验<br/>检查字段归属 / 枚举值 / 口径"]
    G --> H["日期调整<br/>修正画像域分区和时间范围"]
    H --> I["SQL 生成<br/>生成 ODPS SQL"]
    I --> J["SQL 校验<br/>语法 / LIMIT / LIKE / 指标维度"]
    J --> K["最终 SQL 或无法满足"]
```

当前链路特点：

1. 多节点串联，每个节点有独立 LLM prompt 或规则逻辑。
2. 前置节点承担大量业务知识映射，例如主题域、字段、枚举值、指标口径、时间范围。
3. SQL 生成节点要求生成 ODPS SQL，并遵守分区裁剪、JOIN 子查询、LIMIT、LIKE 等规则。
4. 现有 prompt 偏线上生产链路，规则多、上下文长，容易出现维护成本高和信息污染。
5. 画像域表结构较清晰，适合先做单域 agent baseline。

## 5. 画像域数据理解

画像域当前包含 4 张日分区 ADM 表：

| 表 | 完整路径 | 主要能力 |
| --- | --- | --- |
| `adm_asap_base_user_label_dd` | `antsg_asap.adm_asap_base_user_label_dd` | 用户基础画像：状态、年龄、性别、港漂、认证、设备、LBS、生命周期、价值、风控。 |
| `adm_asap_algo_user_label_dd` | `anthk_sg.adm_asap_algo_user_label_dd` | 用户偏好和算法标签：权益偏好、业务偏好、eM+ 潜客、基金潜客、回流潜力、沉默风险。 |
| `adm_asap_pay_user_label_dd` | `antsg_asap.adm_asap_pay_user_label_dd` | 交易行为：交易金额、交易笔数、绑卡、充值、交易场景、理财等。 |
| `adm_asap_other_action_user_label_dd` | `antsg_asap.adm_asap_other_action_user_label_dd` | 非交易行为：登录、活跃、领券、核销、push 互动、页面点击、商户关注。 |

核心规则：

1. 所有表都有 `dt` 分区，格式为 `yyyyMMdd`。
2. 4 张表通过 `user_id + dt` 关联，关系近似 1:1。
3. 优先单表查询，只有用户问题需要跨表字段组合时才 JOIN。
4. 多表 JOIN 时，应先在每张表子查询中完成 `dt` 和业务条件过滤，再按 `user_id + dt` JOIN。
5. 用户数默认使用 `COUNT(DISTINCT user_id)`。
6. 画像域 `_dd` 表短期默认使用 `dt = max_pt('完整表名')`，除非评测或输入明确要求固定业务日期。
7. 常见业务词必须按文档映射，例如：
   - 港漂用户 -> `is_hk_drifter = 'CX'`
   - 永久居民 / 本地用户 -> `is_hk_drifter = 'AX'`
   - 高价值用户 -> `user_value LIKE '1%'`
   - 低价值用户 -> `user_value LIKE '8%'`
   - 新手期 -> `life_cycle = '1'`
   - 成长期 -> `life_cycle = '2'`
   - 沉默期 -> `life_cycle = '5'`
   - eM+ 高潜 -> `em_potential_segment = '高潜'`
   - 基金高潜 -> `fund_potential_segment = '高潜'`
   - 沉默风险高 -> `silence_risk_level = 'high'`

## 6. 技术方案

### 6.1 总体策略

采用 ReFoRCE P0 短期框架，但改造成画像域业务版本：

```mermaid
flowchart TD
    A["用户自然语言查询<br/>当前 P0 默认画像域"] --> B["画像域 markdown 输入<br/>Schema总览 + 4张表明细"]
    B --> C["知识文档转化节点<br/>markdown -> schema registry"]
    C --> D["Compact Context 构造<br/>相关表 / 字段 / 映射 / 口径"]
    A --> E["中文 Schema Summary<br/>问题意图 / 选表 / 字段 / JOIN / dt / 风险点"]
    D --> E
    E --> F["多候选 SQL 生成<br/>Claude 生成 N 条 ODPS SQL"]
    F --> G["静态 SQL 校验<br/>表字段 / dt / JOIN / 枚举 / 聚合 / LIMIT"]
    G --> H["LLM Selector<br/>基于候选 SQL + 校验结果选择最终 SQL"]
    H --> I["最终 SQL<br/>或 目前用户查询无法满足"]
    I --> J["评测与错误归因<br/>对照30题预期分析"]
```

现阶段不追求完整执行反馈闭环，因为当前只有表结构和业务评测集，没有真实数据。

### 6.2 数据输入

需要新增画像域任务输入格式，建议为 JSON / JSONL：

```json
{
  "id": "U001",
  "domain": "画像域",
  "difficulty": "简单",
  "question": "昨天iOS和安卓的用户各有多少",
  "expected_analysis": {
    "semantic": "...",
    "tables": "...",
    "sql_complexity": "..."
  }
}
```

`expected_analysis` 只用于评测和错误分析，不应直接注入 SQL 生成 prompt。

### 6.3 知识文档转化与上下文构造

线上输入保持为业务 markdown。系统需要增加一个“知识文档转化节点”，负责从画像域 markdown 中抽取结构化 schema registry，再基于 registry 构造 prompt 所需上下文。

这个节点的目标是：

1. 不改变业务同学的文档维护方式，业务侧继续维护 markdown。
2. 在工程链路中自动抽取表、字段、类型、值域、指标口径、业务词映射、JOIN 规则和 SQL 示例。
3. 为后续 schema summary、SQL 生成、静态校验提供统一知识源。
4. 保留抽取来源，记录每条结构化知识来自哪个 markdown 文件和章节，方便追溯。

从 schema registry 中构造两类上下文：

1. 全局画像域规则上下文：4 表简介、JOIN 规则、dt 规则、常见指标口径、业务术语映射。
2. 表级字段上下文：每张表的字段名、中文名、类型、值域、关键注意事项。

短期可以先使用规则解析 + 少量 LLM 辅助抽取。若抽取失败，可回退到 markdown 原文片段，但主链路目标仍是让 schema registry 成为统一知识中间层，避免每次都把全文注入 prompt。

### 6.4 中文 Schema Summary Prompt

目标不是直接生成 SQL，而是压缩业务上下文，输出：

```text
[问题意图]
[应使用表]
[相关字段]
[业务词映射]
[指标口径]
[JOIN 方案]
[时间与分区]
[SQL 结构建议]
[风险点]
```

这个节点要重点解决：

1. 业务词到字段和值的映射。
2. 单表 / 多表判断。
3. JOIN key 和分区规则。
4. 聚合粒度和返回形态。

### 6.5 中文 SQL Generation Prompt

SQL 生成 prompt 必须面向业务同学可维护，使用中文写法。

核心要求：

1. 只基于画像域文档提供的表、字段、枚举值和口径生成 SQL。
2. 不允许编造字段、枚举值、表名。
3. 无法满足时返回 `目前用户查询无法满足：原因`。
4. 输出 ODPS / MaxCompute SQL，不输出 Markdown 或解释。
5. 所有表必须加 `dt` 分区。
6. 用户数使用 `COUNT(DISTINCT user_id)`。
7. 多表 JOIN 使用 `user_id + dt`。
8. 多表 JOIN 时每张表先做子查询过滤和列裁剪。

### 6.6 静态 SQL 校验

没有真实数据时，优先做静态校验，而不是 mock 执行。

静态校验应覆盖：

1. 表名是否属于画像域 4 张表。
2. 字段是否存在于对应表。
3. 是否存在 `dt` 分区过滤。
4. 多表 JOIN 是否包含 `user_id` 和 `dt`。
5. 用户数是否使用 `COUNT(DISTINCT user_id)`。
6. 是否误用字段归属，例如把偏好字段写到 base 表。
7. 是否伪造枚举值。
8. 是否符合 topN / ORDER BY / LIMIT 规则。
9. 无法满足时是否给出合理原因。

### 6.7 Selector

由于没有执行结果，selector 不比较 CSV，而是比较：

1. 用户问题。
2. schema summary。
3. 候选 SQL。
4. 静态校验结果。
5. 候选之间的业务语义差异。

selector 输出：

```text
[selected_sql]
候选文件名

[reason]
选择理由，说明表、字段、JOIN、指标口径为何更正确
```

### 6.8 关于 mock 数据

短期不优先 mock。

原因：

1. 当前评测核心是业务语义映射和 SQL 结构，不是执行结果。
2. mock 数据容易让模型在小数据上跑通，但掩盖字段口径、枚举映射、JOIN 规则错误。
3. 没有真实分布时，mock 执行结果不能作为业务正确性指标。

后续可以增加小型 mock 数据，仅用于验证 SQL 语法、JOIN、聚合和 LIMIT 是否可执行，不作为准确率主评估依据。

## 7. 评测方案

短期评测维度：

1. 选表是否正确。
2. 字段是否正确。
3. 业务词映射是否正确。
4. 指标口径是否正确。
5. JOIN 是否正确。
6. 分区规则是否正确。
7. 聚合、GROUP BY、ORDER BY、LIMIT 是否符合问题。
8. 是否存在字段或枚举伪造。

初期可以用人工评审 + LLM judge 双轨。等静态规则稳定后，再做规则化评分。

## 8. 非目标

当前阶段暂不做：

1. 多主题域混合查询。
2. 投放域 / push 域 / 策略域适配。
3. 真实 ODPS 执行。
4. 线上 RAG 系统接入。
5. 大规模流程重构。
6. 基于 mock 数据的结果准确率评测。

## 9. 当前开放问题

1. 评测时 `dt` 应固定为某个业务日期，还是统一使用 `max_pt('完整表名')`？
2. 30 条评测集是否需要标准 SQL gold？
3. LLM judge 是否可以读取评测集中的 A/B/C 分析作为判分依据？
4. 无法满足类输出是否纳入评测，还是所有 30 条都要求生成 SQL？
5. 线上最终是否希望保留意图解析 / 替换 / 校验节点，还是用 agent pipeline 合并部分节点？
