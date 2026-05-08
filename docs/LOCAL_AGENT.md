# Local Text2SQL Agent Guide

这份文档只说明团队本地测试需要的最短路径：目录结构、环境配置、运行方式和输出结果。历史实验、公开榜单和旧脚本不在这里展开。

## 目录

```text
.
├── run_online_agent.py              # 运行入口
├── build_domain_registry.py         # 业务 markdown -> domain registry
├── online_agent/                    # agent 主链路
├── configs/                         # 节点模型和域配置
├── data/
│   ├── profile_eval/                # 画像域结构化资产
│   ├── domain_registries/           # 投放域 / push 域 registry
│   ├── 画像域表合并/
│   ├── 投放域表合并/
│   └── push域表合并/
├── docs/
├── requirements.txt
└── .env.example
```

日常测试只需要关注：

- `run_online_agent.py`
- `configs/online_agent_v1_2.json`
- `.env`
- 输入 CSV
- 输出目录里的 `run_report.csv`

## 环境

推荐使用 Python 3.10：

```bash
conda create -n reforce python=3.10 -y
conda activate reforce
pip install -r requirements.txt
```

## 配置

复制一份本地环境变量文件：

```bash
cp .env.example .env
```

`.env` 只放密钥和 endpoint，不提交到 git。常用配置：

```bash
MOONSHOT_BASE_URL=https://api.moonshot.ai/v1
MOONSHOT_API_KEY=your-moonshot-api-key

SIMPLEAI_BASE_URL=https://key.simpleai.com.cn/v1
SIMPLEAI_API_KEY=your-simpleai-api-key
```

节点模型默认写在：

```text
configs/online_agent_v1_2.json
```

当前默认分工：

- 小模型节点：`router`、`clarifier`、`date_adjuster`、`schema_summary`、`llm_validator`
- 大模型节点：`sql_generation`、`selector`

如需临时覆盖某个节点模型，可以使用环境变量：

```bash
LLM_NODE_SQL_GENERATION_PROVIDER=simpleai
LLM_NODE_SQL_GENERATION_MODEL=claude-opus-4-6
LLM_NODE_ROUTER_PROVIDER=moonshot
LLM_NODE_ROUTER_MODEL=moonshot-v1-128k
```

## 新增 LLM API

如果新接口兼容 OpenAI Chat Completions 协议，通常不需要改代码，只需要改两处：

1. 在 `.env` 增加 endpoint 和 key：

```bash
OPENAI_COMPATIBLE_BASE_URL=https://your-api-host/v1
OPENAI_COMPATIBLE_API_KEY=your-api-key
```

2. 在 `configs/online_agent_v1_2.json` 中，把需要切换的节点改成：

```json
{
  "provider": "openai_compatible",
  "model": "your-model-name"
}
```

也可以临时用环境变量覆盖单个节点：

```bash
LLM_NODE_SQL_GENERATION_PROVIDER=openai_compatible
LLM_NODE_SQL_GENERATION_MODEL=your-model-name
```

如果要接入一个全新的 provider，变更位置是：

- `chat.py`：在 `GPTChat.resolve_provider()` 里增加 provider 分支，读取对应的 `XXX_BASE_URL` 和 `XXX_API_KEY`。
- `.env.example`：补充新 provider 的环境变量示例。
- `configs/online_agent_v1_2.json`：把相关节点的 `provider/model` 配成新 provider。

如果新接口不是 OpenAI Chat Completions 协议，还需要在 `chat.py` 中调整请求 payload 和响应解析。

## 运行

### 单条 query

适合快速调试一条问题：

```bash
python3 run_online_agent.py \
  --question '昨天push任务的打开率是多少' \
  --output-dir output/single-query-smoke \
  --no-selector
```

### 批量 CSV

适合测试同学批量传入 query：

```bash
python3 run_online_agent.py \
  --input-file data/test_queries.csv \
  --output-dir output/batch-query-smoke \
  --limit 20 \
  --no-selector
```

CSV 至少需要包含 `query` 或 `question` 列。`id` 可选，不传时系统会自动生成 `Q001`、`Q002`。

示例：

```csv
id,query
T001,昨天push任务的打开率是多少
T002,首页feeds昨天曝光点击量是多少
```

常用筛选参数：

```bash
--limit 20
--offset 0
--sample-ids T001,T003
--resume
```

说明：

- `--limit`：最多跑多少条。
- `--offset`：从第几条开始跑。
- `--sample-ids`：只跑指定 ID，优先级高于 `limit/offset`。
- `--resume`：复用已有 `log.json`，避免重复调用模型。

## 输出

每次运行会生成一个输出目录：

```text
output/<run-name>/
├── run_report.csv          # 给测试同学看的汇总表
├── run.json                # 完整结构化结果
├── run_summary.json        # 运行摘要
├── timing_report.json      # 耗时明细
├── run_events.jsonl        # 增量事件日志
└── <id>/
    ├── log.json
    ├── result.sql
    └── schema_summary.md
```

测试优先看：

```text
run_report.csv
```

关键列：

- `id`
- `query`
- `sql`
- `res`
- `status`
- `message`
- `time_cost`
- `route_domains`
- `output_sql_path`

`res/status` 表示当前链路状态，不等同于真实业务执行结果。后续接入 mock 或真实执行器后，可以再把执行结果补充到 `res`。

## Registry 构建

当投放域或 push 域 markdown 有更新时，重新生成 registry：

```bash
python3 build_domain_registry.py --domain marketing
python3 build_domain_registry.py --domain push
```

输出位置：

```text
data/domain_registries/
```

画像域资产当前已经生成在：

```text
data/profile_eval/
```

日常跑 agent 不需要手动重建画像域资产。

## 常见问题

如果命令找不到依赖：

```bash
pip install -r requirements.txt
```

如果模型调用失败，先检查：

- `.env` 是否存在。
- 对应 provider 的 API key 是否已填写。
- `configs/online_agent_v1_2.json` 中节点 provider 和 model 是否匹配。

如果批量跑到一半中断，可以用同一个输出目录加 `--resume` 继续：

```bash
python3 run_online_agent.py \
  --input-file data/test_queries.csv \
  --output-dir output/batch-query-smoke \
  --limit 20 \
  --resume
```
