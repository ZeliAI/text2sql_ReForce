# P0 Design

这份文档只覆盖 P0 两项改造：

1. **生成前 schema summarization / filtering**
2. **LLM-based final choose / selector**

目标不是一步到位复刻整篇论文，而是：

- 在不推翻现有可运行链路的前提下
- 先提高 candidate 质量
- 再提高最终 candidate 选中的概率

---

## 1. P0 总目标

当前链路已经证明两件事：

1. 候选里有时会出现正确 SQL，但最终没被选中。
2. 直接把 `db_desc` 整块塞给生成模型，噪声太高，影响首轮 candidate 质量。

所以 P0 的目标是双向修正：

- **输入侧降噪**：先做一轮 schema summary/filtering
- **输出侧提纯**：在多个 candidates 中做更可靠的 final choose

---

## 2. 设计原则

### 2.1 不立刻推翻现有骨架

P0 阶段不重写整个 `run.py -> agent.py -> vote_result()` 控制流。

原因：

- 现有链路已经能跑 benchmark
- 现在最需要的是先建立更强 baseline
- 大规模 orchestration 重构留给 P1

### 2.2 新阶段要单独命名、单独落日志

P0 新增的两步都必须有独立日志，不要继续混在 `self_refine` 里。

需要明确区分：

- 原始 schema 输入
- summary/filter 输出
- candidate SQLs
- final choose 输入
- final choose 决策理由

### 2.3 selector 是 judge，不是再生成一遍 SQL

final choose 阶段不应该变成“让模型再写一版 SQL”。

它应该只做：

- 看 question
- 看 summary schema
- 看 candidates SQL
- 看 candidates CSV
- 选一个最合理的候选

输出：

- `selected_sql_filename`
- `reason`

---

## 3. P0-1: Schema Summarization / Filtering

## 3.1 放置位置

应放在：

- `run.py` 拿到 `table_info` 之后
- 主生成前
- vote 前共享一次，不要每个 candidate 重复做

也就是说，新的流程是：

1. `question`
2. `table_info` / `db_desc`
3. `schema_summary = summarize_schema(question, table_info)`
4. 多 candidate SQL 生成时，都消费同一个 `schema_summary`

而不是每个 vote 线程各自总结一次。

## 3.2 输入

输入内容：

- `question`
- 原始 `table_info` / `db_desc`

## 3.3 输出

建议输出为结构化文本，而不是一开始就强求 JSON。

建议格式：

```text
[Relevant Tables]
- table_a: why relevant
- table_b: why relevant

[Relevant Columns]
- table_a.col_1: reason
- table_b.col_2: reason

[Possible Join Keys]
- table_a.id = table_b.a_id
- ...

[Cautions]
- metric is per-player, not per-ball
- avoid dropping rows with inner join on wickets
```

这样好处是：

- 易读
- 易直接拼进 prompt
- 模型不容易因为 JSON 格式失败而崩掉

## 3.4 Prompt 目标

这个 summary prompt 不应该直接让模型写 SQL。

它的职责应限定为：

1. 识别最相关表
2. 识别最相关列
3. 推测关键 join path
4. 点出任务里的聚合口径和风险点
5. 删除明显无关 schema 噪声

## 3.5 下游 prompt 要同步修改

这是 P0 的关键点。

主生成 prompt 不再直接写成：

- “Here is full schema, write SQL”

而应改成：

- “Here is summarized schema context produced by a previous analysis step”
- “Prefer using the summarized relevant tables/columns/join keys below”
- “If summary misses something, fall back cautiously to raw schema”

建议主 prompt 结构变成：

1. `Question`
2. `Schema Summary`
3. `Raw Schema (optional, truncated or secondary)`
4. `SQL generation instructions`
5. `Semantic checklist`

## 3.6 是否还保留 raw schema

P0 阶段建议：**保留，但降级**。

也就是：

- 主上下文以 `schema_summary` 为主
- 原始 `table_info` 作为 secondary context
- 明确提示“优先依赖 summary，再必要时回看 raw schema”

这样更稳，避免 summary 出错时完全失去补救空间。

## 3.7 资源消耗

新增 1 次 LLM 调用 / 每个样本。

但因为这个 summary 是所有 vote candidates 共享的，所以成本相对可接受。

如果当前：

- `NUM_VOTES=3`
- `MAX_ITER=3`

那新增的 summary 通常远低于主生成总成本。

---

## 4. P0-2: LLM-based Final Choose / Selector

## 4.1 放置位置

放在：

- 所有 candidate 都跑完之后
- `vote_result()` 内部
- 替换当前“弱 final_choose”逻辑

保留现有的“结果完全一致 -> 直接选”捷径。

也就是说：

1. 如果多个 candidate 结果完全一致，保留当前 fast path。
2. 如果没有稳定共识，再进入 `selector_judge()`。

## 4.2 输入

selector 输入应包含：

- `question`
- `schema_summary`
- 每个 candidate 的 SQL
- 每个 candidate 的 CSV 结果
- 可选：candidate 执行状态、是否经过修正、是否有异常

建议不要把完整 raw schema 全塞进去。

selector 更需要：

- summary schema
- 结果表
- SQL 本身

## 4.3 输出

建议要求模型输出：

```text
[selected_sql]
2result.sql

[reason]
Candidate 2 uses the full join key and returns the requested entity name instead of an id.
```

最终代码只消费 `selected_sql`。

`reason` 用来写日志。

## 4.4 selector prompt 的判断顺序

要强约束，不让它自由发挥。

建议 checklist：

1. 是否返回了题目要求的列/实体
2. 是否返回了正确的结果形状
3. SQL 的 aggregation grain 是否匹配任务
4. join key 是否完整
5. 是否有明显会静默丢行的 inner join
6. 若多个都能执行，优先选择语义更贴近题意者

## 4.5 selector 资源消耗

建议先做 **单次多候选判别**。

也就是 1 个样本额外只调用 1 次 LLM。

相对成本：

- 比再生成 1 个 candidate 便宜
- 比让 selector 再写 SQL 便宜很多
- 足够先验证是否能把 `Pass@k` 转成 `Final score`

## 4.6 selector 能判断准吗

结论：**能提升，但不能盲信。**

更准确地说：

它擅长：

- 区分 `name` vs `id`
- 区分 scalar vs table
- 区分明显错误的 join / aggregation
- 在候选差异比较明显时选出更合理者

它不擅长：

- 所有候选都长得很像时做精细业务判别
- 没有 summary schema 支撑时理解复杂统计定义

所以 selector 成败高度依赖：

- summary schema 质量
- prompt checklist 质量

这也是为什么 P0 的两项改造要一起做。

---

## 5. 代码落点

## 5.1 建议新增函数/方法

### `run.py`

建议新增或插入：

- `build_schema_summary(question, table_info, args)`

职责：

- 为每个样本只调用一次
- 返回 `schema_summary`
- 落 summary 日志

### `agent.py`

建议新增：

- `selector_choose(...)`

职责：

- 输入所有 candidate SQL + CSV
- 调用 judge LLM
- 返回最终选中的 `sql filename`
- 落 `selector.log`

### `prompt.py`

建议新增：

- `get_schema_summary_prompt(...)`
- `get_selector_prompt(...)`

并改造：

- 主生成 prompt，新增 `schema_summary` 输入位

## 5.2 建议新增日志文件

每个样本目录新增：

- `schema_summary.log`
- `schema_summary.txt`
- `selector.log`

可选新增：

- `selector_input.txt`
- `selector_output.txt`

这样调试时非常清楚。

---

## 6. P0 改造后的流程

P0 结束后，理想流程应变成：

1. 读取 `question + raw schema`
2. 调用 `schema summarizer`
3. 得到 `schema_summary`
4. 用 `schema_summary + raw schema secondary context` 生成多个 candidates
5. 执行 candidates
6. 对异常 SQL 仍沿用当前 self-refine 机制
7. 所有 candidates 跑完后：
   - 有稳定一致结果 -> 直接选
   - 无稳定一致结果 -> LLM selector 判别
8. 写最终 `result.sql/result.csv`

---

## 7. 这一步暂时不做什么

为了保持 P0 收敛，先明确不做：

- 不改 candidate generation 的主位置
- 不引入显式 confidence router
- 不把 column exploration 改成动态触发
- 不重写整个 `self_refine()` 主循环
- 不接 BM25 / 关键词召回

这些都留给 P1/P2。

---

## 8. 成功标准

P0 做完后，优先看这几个信号：

1. `Pass@k` 是否提升
2. `Final score` 是否更接近 `Pass@k`
3. `selector` 是否能保住像 `local020` 这种已有正确候选的样本
4. 首轮 candidate 是否更少出现明显错表、错列、错粒度
5. 日志是否更容易区分：
   - 输入压缩问题
   - 生成问题
   - 选择问题

---

## 9. 一句话版方案

P0 不大拆框架，只做两刀：

- **先压输入**：schema summary/filtering
- **再提输出**：LLM selector/final choose

这样能先把当前链路从“能跑”拉到“更像一个可靠 baseline”，同时为 P1 的主流程重排铺路。
