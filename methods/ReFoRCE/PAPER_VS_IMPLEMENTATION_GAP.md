# Paper vs Current Implementation

这份文档只回答两个问题：

1. 当前 GitHub repo 作为论文官方仓库，但 Lite SQLite 这条执行链路已经明显简化，这样是否影响复现的公允性。
2. 论文流程与当前实现流程逐阶段对照，明确每一步理论上该放哪里、现在实际放在哪里、为什么会错位。

## 1. 这算不算公允复现

先说结论：

**如果把“直接运行官方 GitHub repo 提供的脚本”当作论文方法的完整复现，那是不完全公允的。**

更准确的说法是：

- 这份 repo 当然是作者提供的，具有官方性。
- 但它暴露出来的 Lite SQLite 运行链路，更像是一个**面向实验复现和批量评测的简化工程入口**。
- 这条链路并不等价于“论文里逐阶段展开的完整 agent workflow”。

所以这里要区分两件事：

1. **复现实验结果**
   - 如果作者的最终分数就是基于这套简化后的预处理输入和脚本跑出来的，那么“照着 repo 跑”在工程上是复现实验设置。
2. **复现论文方法本身**
   - 如果你要复现的是论文描述的 agent 流程、阶段顺序、决策逻辑，那当前 repo 暴露出的 Lite 路径并不完整。

换句话说：

**repo 可以是官方的，但官方 repo 也可能只放出了一个已经折叠过的信息流和执行入口。**

这在学术工程里不罕见，但会带来一个现实问题：

- 对“想复现实验分数”的人，它是方便的。
- 对“想复现方法机制”的人，它是不够透明的。

### 1.1 为什么说它影响公允性

影响公允性的点，不在于作者“不能简化”，而在于：

- 论文里强调的是一个多阶段 agent 方法。
- repo 里 Lite SQLite 路径更像一个预处理输入驱动的生成式脚本。
- 如果没有额外说明，读者会自然默认：`repo main path ~= paper method`。

但当前我们已经确认，至少下面这些地方并不一致：

- schema 压缩/筛选的阶段位置不一致
- candidate generation 的阶段位置不一致
- self-refine 的职责边界不一致
- vote/final choose 的实现强度明显弱于论文叙述带来的预期

所以更公平的表述应该是：

**这份 repo 更接近“作者用于复现实验的一套可运行实现”，而不是“逐模块忠实展开论文 agent 机制的参考实现”。**

这不是说 repo 没价值，而是说：

- 用它复现“结果”是一个维度
- 用它复现“方法”是另一个维度

两者不能自动画等号。

### 1.2 对我们当前工作的意义

这件事对我们很重要，因为它决定了后续改造目标：

- 如果目标是“先跑通、拿一个可比较 baseline”，那沿用 repo 当前路径是合理的。
- 如果目标是“构建一个更贴近论文范式的 text2sql agent”，那必须重排主流程，而不是只在现有 prompt 上打补丁。

## 2. 论文流程 vs 当前实现流程

下面这张表，重点比较的是**阶段顺序**和**模块职责**。

| 阶段 | 论文流程中应有的位置 | 当前实现里实际位置 | 当前实现做法 | 为什么会错位 | 影响 |
|---|---|---|---|---|---|
| 任务输入 | 从 benchmark 原始问题开始，进入 agent 流程 | 在 `run.py` 开头直接读 `omnisql_spider2_sqlite.json` | 直接使用预处理后的 `question + db_desc + db_id` | Lite 路径复用了 OmniSQL 风格输入文件 | 丢失了“原始任务到 agent 决策”的前半段透明度 |
| 初始 schema 信息组织 | 进入 SQL 生成前，应先做一轮 schema compression / summarization / filtering | 当前在 `get_table_info()` 后，基本直接把 `db_desc` 喂进 prompt | 更像“整份 schema 描述直接塞给模型” | repo 依赖预处理好的 `db_desc`，没有在线压缩调度层 | prompt 负担大，噪声高，模型更容易抓错重点 |
| 第一轮 schema 筛选 | 理应在 text2sql 生成前，先做 task-aware schema 筛选 | 现在只有离线 OmniSQL 风格预处理；运行时缺少一轮明确的在线再筛选 | 没有显式“先总结再生成”的阶段 | 当前骨架以生成函数为中心，不是以 planner/retriever 为中心 | 和论文强调的信息压缩逻辑不一致 |
| candidate generation | 应在主生成阶段就并行生成多个 SQL candidates | 当前 `do_vote` 是并发跑多个完整分支，每个分支各自做生成/执行/修正 | 不是“先出 candidates，再统一分析”，而是“多个独立小流程并行” | 代码骨架按线程并发 `execute()` 写成了多条平行主链 | candidates 的调度、比较、置信度判断都被弱化 |
| confidence / uncertainty 判断 | 生成出多个 candidates 后，应根据 low confidence 决定是否进入下一轮 exploration | 当前几乎没有显式 confidence 层 | 只有 vote、结果比较、少量 self-consistency | repo 没有把不确定性建成单独状态机 | 无法做到“候选不好 -> 再探索列/信息”的闭环 |
| column exploration | 理应在 candidate 不足或不稳定时触发，作为补充信息获取步骤 | 当前是一个可选前置分支 `do_column_exploration` | 更像“先做或不做”的固定开关 | 实现上是可选预处理，不是动态触发 | 与论文中的按需探索逻辑不一致 |
| SQL execution | 用于验证 candidates，并收集异常结果 | 当前位置基本合理 | 生成后立即执行 SQL | 这一层本身没大问题 | 能提供真实执行反馈 |
| self-refine | 应作用于“执行后异常的 candidate”，做 candidate-level 修正 | 当前被放进主生成循环 `self_refine()`，几乎成了默认生成方式的一部分 | 先生成一条 SQL，执行，报错再修；但整个主生成链路都挂在 self_refine 名下 | 代码结构以 `self_refine()` 为主入口生长出来 | self-refine 的职责被扩大，和论文中的位置不一致 |
| self-consistency / semantic checking | 应在 candidate 或结果层辅助判断正确性 | 当前只对部分成功执行结果做一轮 prompt 再检查 | 更偏结果重复性和格式一致性 | 现有实现较轻 | 对“能执行但语义错”的问题帮助有限 |
| voting / consensus | 应在多个候选之上做真正的共识判断 | 当前主要按 `result.csv` 是否一致来分组 | 无共识时，`final_choose` 很弱，容易退化成拿第一个候选 | 实现偏工程捷径 | 候选里有对的，最终也可能丢掉 |
| final choose | 应该是一个认真比较候选 SQL 与结果的判别阶段 | 当前只有在特定条件下才走较强选择，否则很容易退化 | `final_choose` 不是强判别器 | 逻辑过于简化 | 直接影响最终分数，尤其是 pass@k 转 final score 的能力 |

## 3. 当前实现流程的真实样子

如果把当前 Lite SQLite 实际执行过程压成一句话，它更像：

**预处理输入 -> 直接喂大块 schema prompt -> 多个并发分支各自生成 SQL -> 各自执行 -> 各自做有限修正 -> 最后按结果做弱投票/弱选择。**

而论文更像：

**任务理解 -> 信息压缩/筛选 -> 生成多个 candidates -> 基于低置信度触发进一步 exploration -> 对异常 candidate 做 refine -> 在候选层做更强的共识与最终选择。**

这两者最大的差别不是某一个 prompt 少写了一句，而是：

**一个是“生成函数驱动”的流程，一个是“agent 状态调度驱动”的流程。**

## 4. 为什么 repo 会自然滑向现在这种实现

我认为主要有四个原因：

1. **为了批量评测方便**
   - 预处理输入文件、固定脚本入口、统一输出目录，都很适合大规模跑 benchmark。
2. **为了复用 OmniSQL 风格输入**
   - 这减少了在线召回和在线信息组织的复杂度。
3. **为了降低工程复杂度**
   - 把很多阶段折叠进 `self_refine()` 和 `vote_result()`，入口更少，更容易跑通。
4. **论文与仓库的目标不同**
   - 论文强调方法机制。
   - 仓库更像实验实现和复现壳子。

## 5. 我们后续改造时应该怎么用这张表

建议把后续改造分成两类，不要混着做：

### 5.1 结果导向的小修小补

适合短期拿 baseline：

- 强化 prompt
- 改善 selector / final choose
- 增加更稳的日志
- 增加简单 schema / 文档召回

### 5.2 方法导向的流程重排

适合追求更贴近论文：

1. 在主生成前增加在线 schema summarization / filtering
2. 把 candidate generation 从 `self_refine()` 前移出来
3. 增加 candidate-level confidence / uncertainty 判断
4. 把 column exploration 改成按需触发，而不是静态开关
5. 把 self-refine 明确限制为“异常 candidate 修复器”
6. 把 final choose 改成真正的候选判别器

## 6. 当前最重要的判断

如果只保留一句最重要的话，那就是：

**当前这份官方 repo 的 Lite SQLite 主路径，更像“作者为了复现实验而提供的简化实现”，而不是“论文 agent 机制的逐阶段忠实实现”。**

这也是为什么我们现在会感觉：

- 代码能跑
- 结果也能出
- 但方法味道和论文描述差得不少

这种差距不是错觉，而是实现层级上的真实偏移。
