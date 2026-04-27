# Refactor Priorities

这份文档承接：

- [PAPER_VS_IMPLEMENTATION_GAP.md](/Users/ying/Documents/老凤/text2sql/ReForce/ReFoRCE/methods/ReFoRCE/PAPER_VS_IMPLEMENTATION_GAP.md)

目标是把后续改造拆成两类：

1. **结果提升的小修**：不重排主流程，优先提升可用性和分数。
2. **方法对齐的大改**：按论文思路重排 agent workflow。

这样做的原因很简单：

- 小修适合快速拿 baseline、验证方向。
- 大改适合真正把系统做成你想要的 text2sql agent。
- 如果两类改动混在一起，很容易既改不快，也改不清楚。

## 1. 总体建议

先说最实际的建议：

### 1.1 如果目标是短期看效果

优先做：

- schema 再压缩 / 再筛选
- final choose / selector 增强
- 更强的日志和诊断
- 简单关键词或 BM25 召回

这些改动都不需要一下子推翻现有 `run.py + agent.py` 骨架。

### 1.2 如果目标是贴近论文方法

优先做：

- 把 candidate generation 从 `self_refine()` 里拆出来
- 增加 candidate-level confidence / uncertainty 判断
- 把 column exploration 改成按需触发
- 把 self-refine 改回“异常 candidate 修复器”
- 把 final choose 改成真正的候选判别器

这些已经不是调 prompt 级别，而是 orchestration 重构。

## 2. 优先级表

| 优先级 | 改造项 | 类型 | 为什么重要 | 预期收益 | 风险/成本 |
|---|---|---|---|---|---|
| P0 | 增强 final choose / selector | 小修 | 当前已经出现候选里有正确答案但最终选错 | 能直接把 `Pass@k` 往 `Final score` 转化 | 中等 |
| P0 | 在 SQL 生成前增加一轮 schema summarization / filtering | 小修到中改 | 当前 schema 直接整块塞给模型，噪声过高 | 提升候选首轮质量 | 中等 |
| P0 | 引入简单关键词/BM25 召回 | 小修到中改 | 与你的真实需求更一致，也能减少 prompt 冗余 | 提高相关 schema / 文档命中率 | 中等 |
| P1 | 把 candidate generation 从 `self_refine()` 前移 | 大改 | 当前候选生成位置与论文不一致 | 更贴近论文主流程 | 高 |
| P1 | 增加 candidate-level confidence 判断 | 大改 | 论文式的 exploration 触发依赖低置信度信号 | 让后续 exploration 更有依据 | 高 |
| P1 | 把 column exploration 改成动态触发 | 大改 | 现在只是静态开关，论文里更像按需使用 | 可能显著改善难题 | 高 |
| P1 | 把 self-refine 限制为“异常 candidate 修复器” | 大改 | 现在 self-refine 位置和职责都偏了 | 方法一致性更强 | 中高 |
| P2 | 改善 self-consistency 的语义审查能力 | 小修 | 现在更偏执行正确，不够懂业务语义 | 提高“能跑但错”这类题的纠错能力 | 中等 |
| P2 | 改进日志结构，明确区分阶段 | 小修 | 现在能排障，但阶段边界还不够清楚 | 提高调试效率 | 低 |
| P3 | 再做 prompt 微调 | 小修 | 仍有帮助，但不是当前最大瓶颈 | 小幅提升 | 低 |

## 3. 我建议的执行顺序

### 阶段 A：先做最值当的小修

这阶段的目标不是“完全对齐论文”，而是：

**尽快把现有链路从“能跑”拉到“更像一个靠谱 baseline”。**

建议顺序：

1. **增强 final choose / selector**
   - 这是当前最直接的失分点。
   - Claude 的 `local020` 已经证明：正确候选出现了，但最终没选中。

2. **在输入侧增加一轮 schema summarization / filtering**
   - 即使暂时不完全重构，也应该在进入主生成前再压一次 schema。
   - 这个点与你的判断一致，而且对 prompt 质量很关键。

3. **接入简单关键词/BM25 召回**
   - 这会让系统从“预处理输入驱动”更接近“真实 agent 在线工作流”。
   - 也更符合你最初的需求。

4. **补强日志结构**
   - 把“输入筛选 -> 候选生成 -> 执行 -> refine -> choose”明确打点。
   - 后面大改时会省很多时间。

### 阶段 B：做方法对齐的大改

这阶段的目标是：

**从当前 repo 骨架，重排成更接近论文的 agent flow。**

建议顺序：

1. **拆出 candidate generation 阶段**
   - 不再让 vote 分支各自跑一整条主链。
   - 先统一生成一批 candidates。

2. **引入 confidence / uncertainty 判断**
   - 每个 candidate 或 candidate set 给一个置信度信号。
   - 这是触发 exploration/refine 的前提。

3. **把 column exploration 改成动态触发**
   - 当候选质量差或不确定性高时，再去探索列和补信息。

4. **把 self-refine 下沉到异常 candidate 层**
   - 只修报错或明显异常的 SQL。
   - 不再把它当成默认主生成入口。

5. **重写 selector / final choose**
   - 从“结果表比对 + 弱选择”升级成“候选语义判别器”。

## 4. 哪些改动最可能马上提升分数

如果只从“短期提升效果”出发，我的排序是：

1. **selector / final choose**
2. **schema 再压缩 / 再筛选**
3. **简单召回**
4. **self-consistency 强化**
5. **prompt 微调**

原因是：

- 当前已经证明候选里有对的，说明不是全靠换模型。
- 先把“已有正确候选”保住，比再去盲目加更多生成更划算。
- 而 schema 噪声问题又会直接影响首轮候选质量，所以排第二。

## 5. 哪些改动最能提升方法一致性

如果只从“贴近论文”出发，我的排序是：

1. **candidate generation 前移**
2. **confidence 判断**
3. **dynamic column exploration**
4. **self-refine 职责回归**
5. **selector 重做**

这几项一旦完成，系统的骨架才会从：

**生成驱动**

变成：

**状态调度驱动**

## 6. 一个现实建议

不要一上来就全量重构。

更稳的做法是：

### 路线 1：先拿实用结果

- 改 selector
- 加 schema summarization
- 加 BM25 / 关键词召回
- 跑小样本对比

### 路线 2：再做论文对齐版

- 新建一条更清晰的 pipeline
- 不强行把所有逻辑都塞回现有 `self_refine()`
- 用新入口实验，不先破坏旧入口

## 7. 当前最推荐的下一步

如果现在就要开始动手，我最推荐的第一步是：

**先做两件事，不多也不少：**

1. **在主生成前增加一轮 schema summarization / filtering**
2. **把 final choose 改成真正的候选判别器**

这两件事有一个很好的特点：

- 一件改输入质量
- 一件改输出选择

它们都能明显改善现有链路，但还不至于立刻把整个框架推翻。

## 8. 一句话版结论

如果要兼顾“快”和“对”，最合理的节奏是：

**先修 selector 和输入压缩，再重排 candidate / refine / exploration 的主流程。**
