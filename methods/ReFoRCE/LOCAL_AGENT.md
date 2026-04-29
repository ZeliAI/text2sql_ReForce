# Local Text-to-SQL Agent Guide

这份文档面向两个场景：

1. 在一台新的机器上，从 git 拉代码、配置 SQLite 和 API、跑通整个流程。
2. 后续需要接更多 LLM API 来源时，知道该改哪里。

## 1. 从零开始拉起一个新环境

### 1.1 拉代码

如果是新机器，先 clone 仓库：

```bash
git clone https://github.com/ZeliAI/text2sql_ReForce.git
cd text2sql_ReForce/methods/ReFoRCE
```

如果你是从官方仓库开始，也可以：

```bash
git clone https://github.com/Snowflake-Labs/ReFoRCE.git
cd ReFoRCE/methods/ReFoRCE
```

### 1.2 创建 Python 环境

推荐用 `conda`：

```bash
conda create -n reforce python=3.10 -y
conda activate reforce
pip install -r requirements.txt
```

如果终端里默认 `python` 不是 Python 3，可以继续使用：

```bash
python3
```

或者在当前 shell 中加载：

```bash
source scripts/use_python3.sh
```

### 1.3 准备 Spider2-Lite SQLite 数据库

Lite SQLite 路径依赖可执行的 `.sqlite` 文件，它们应该放在：

- [spider2-lite/resource/databases/spider2-localdb](/Users/ying/Documents/老凤/text2sql/ReForce/ReFoRCE/spider2-lite/resource/databases/spider2-localdb)

如果这个目录还没有准备好，需要把 Spider2-Lite 的 SQLite 数据库放进去。当前仓库运行时只认这个目录。

检查方式：

```bash
find ../../spider2-lite/resource/databases/spider2-localdb -name "*.sqlite" | head
```

如果能看到一批 `.sqlite` 文件，说明 SQLite 环境已经就绪。

### 1.4 配置 API 接口

把密钥和基础地址放在：

- [`.env`](/Users/ying/Documents/老凤/text2sql/ReForce/ReFoRCE/methods/ReFoRCE/.env)
- [`.env.example`](/Users/ying/Documents/老凤/text2sql/ReForce/ReFoRCE/methods/ReFoRCE/.env.example)

推荐格式：

```bash
MOONSHOT_BASE_URL=https://api.moonshot.ai/v1
MOONSHOT_API_KEY=your-moonshot-api-key

SIMPLEAI_BASE_URL=https://key.simpleai.com.cn/v1
SIMPLEAI_API_KEY=your-simpleai-api-key

PYTHON_BIN=/path/to/your/python
```

说明：

- 新机器可以先复制 `.env.example` 为 `.env`，再按 provider 填值
- `.env` 只放敏感信息和机器相关信息，例如各 provider 的 `*_API_KEY`
- `PYTHON_BIN` 建议指向实际运行环境里的解释器，例如 `conda` 环境中的 `python`
- 不建议把具体模型、并发、任务数也放进 `.env`
- 模型和运行参数放在 [config.env](/Users/ying/Documents/老凤/text2sql/ReForce/ReFoRCE/methods/ReFoRCE/config.env)

如果你要通过 `simpleai` 调 Claude，可以这样配：

```bash
SIMPLEAI_BASE_URL=https://key.simpleai.com.cn/v1
SIMPLEAI_API_KEY=your-simpleai-key
```

这时模型名可以直接写在 `config.env`，例如：

```bash
LLM_MODEL=claude-opus-4-6
```

目前 `simpleai` 这边可直接尝试的模型写法包括：

```bash
LLM_MODEL=claude-opus-4-6
LLM_MODEL=claude-opus-4-7
LLM_MODEL=claude-sonnet-4-6
LLM_MODEL=claude-haiku-4-5-20251001
```

### 1.5 配置运行参数

主要运行参数放在：

- [config.env](/Users/ying/Documents/老凤/text2sql/ReForce/ReFoRCE/methods/ReFoRCE/config.env)

一个常见的 Lite SQLite 配置示例：

```bash
LLM_PROVIDER=moonshot
LLM_MODEL=moonshot-v1-128k
LLM_TEMPERATURE=0.6
LLM_TIMEOUT=120
LLM_MAX_TOKENS=4096
THINK_OR_NOT=false
THINKING_UNSUPPORTED_MODELS=moonshot-v1-128k,moonshot-v1-32k

LLM_RETRY_MAX=8
LLM_RETRY_BASE_SECONDS=2
LLM_RETRY_MAX_SECONDS=30
LLM_TEST_MODE=false

NUM_WORKERS=1
MAX_ITER=1
TASK_LIMIT=10
TASK_OFFSET=0
DO_VOTE=false
NUM_VOTES=3
RANDOM_VOTE_FOR_TIE=false
FINAL_CHOOSE=false

OUTPUT_PATH=output/moonshot-v1-128k-lite-sqlite-10-no-thinking
ADD_TIMESTAMP=true
```

补充说明：

- `run_lite_sqlite.sh` 和 `run_eval.sh` 现在都会自动读取 `.env` 与 `config.env`
- `config.env` 支持 `KEY=value # 注释` 这种行尾注释写法
- 如果不显式传 `OUTPUT_PATH`，脚本会自动生成目录名，格式大致是：

```text
output/<model>-lite-sqlite-<thinking-or-not>-limit<TASK_LIMIT>-offset<TASK_OFFSET>-YYYYMMDD-HHMMSS
```

### 1.6 先跑一个本地 smoke test

这个 smoke test 不依赖 Spider2-Lite 数据库，适合先验证 API 和代码链路是否通。

```bash
cd /path/to/text2sql_ReForce/methods/ReFoRCE
conda activate reforce
python3 -B run_local_demo.py --mock
```

它会创建一个极小 SQLite demo，并写出：

- `output/local-demo/result.sql`
- `output/local-demo/result.csv`
- `output/local-demo/log.json`

如果你想直接调用真实 LLM：

```bash
python3 -B run_local_demo.py --model "$LLM_MODEL"
```

### 1.7 跑通 Lite SQLite 全链路

当 `.env`、`config.env`、SQLite 数据库都准备好之后，直接运行：

```bash
cd /path/to/text2sql_ReForce/methods/ReFoRCE
conda activate reforce
bash scripts/run_lite_sqlite.sh
```

这个脚本会：

1. 自动读取 `.env`
2. 自动读取 `config.env`
3. 只跑 Lite SQLite 子任务
4. 调用 [run.py](/Users/ying/Documents/老凤/text2sql/ReForce/ReFoRCE/methods/ReFoRCE/run.py)
5. 如果没有传 `OUTPUT_PATH`，自动生成一个带模型/模式/limit/offset 的输出目录
6. 在终端打印带时间戳的关键阶段进度，例如当前第几题、是否进入 `schema_summary`、`self_refine`、`vote_merge`

如果 `ADD_TIMESTAMP=true`，最终目录会是：

```text
output/<你的输出名>-YYYYMMDD-HHMMSS
```

### 1.8 评测结果

跑完后，用下面的命令评测：

```bash
bash scripts/run_eval.sh --task lite --log_folder output/<你的实际输出目录>
```

例如：

```bash
bash scripts/run_eval.sh --task lite --log_folder output/moonshot-v1-128k-lite-sqlite-10-no-thinking-20260426-120000
```

## 2. 常用运行方式

### 2.1 只跑几条快速验证

```bash
TASK_LIMIT=3 TASK_OFFSET=10 bash scripts/run_lite_sqlite.sh
```

### 2.2 开启 self-refine 多轮修正

在 `config.env` 中设置：

```bash
MAX_ITER=3
```

### 2.3 开启 vote / 多候选

在 `config.env` 中设置：

```bash
DO_VOTE=true
NUM_VOTES=3
RANDOM_VOTE_FOR_TIE=true
FINAL_CHOOSE=true
```

注意：

- 当前 `run.py` 的 vote 是并发发起多个候选请求
- 如果模型服务端并发额度较小，`NUM_VOTES` 过大容易触发 `429`
- 例如 Moonshot 这边如果组织并发上限是 3，就更适合 `NUM_VOTES=3`

## 3. 测试模式

测试模式主要用于分辨：

- 是模型能力问题
- 还是 prompt 问题
- 还是响应清洗问题
- 还是 API 调用 / 限流问题

开启方式：

```bash
LLM_TEST_MODE=true TASK_LIMIT=1 TASK_OFFSET=10 bash scripts/run_lite_sqlite.sh
```

如果你要手动验证 `local019`，当前数据文件中它对应：

```bash
LLM_TEST_MODE=true TASK_LIMIT=1 TASK_OFFSET=10 LLM_MODEL=kimi-k2.6 THINK_OR_NOT=false LLM_TEMPERATURE=0.6 bash scripts/run_lite_sqlite.sh
```

开启后，每个样本对应的 `log.log` 会额外记录：

- `[LLM call]`
  - 当前模型名
  - temperature
  - 发给 API 的请求 payload
  - 模型原始输出
  - 清洗后的 code blocks
- `[LLM retry]`
  - 重试次数
  - 等待时长
  - 原始错误信息
- `[LLM exception]`
  - 最终抛出的异常

这些日志写在每个样本自己的目录里，例如：

- `output/<run-name>/local019/log.log`

同时，终端会直接打印带时间戳的阶段进度，例如：

```text
[2026-04-29 15:42:10] [1/1] [local019] task_start | model=kimi-k2.6, vote=False, max_iter=1
[2026-04-29 15:42:10] [1/1] [local019] schema_summary_start | model=kimi-k2.6
[2026-04-29 15:45:31] [1/1] [local019] schema_summary_done | output/.../schema_summary.txt
[2026-04-29 15:45:31] [1/1] [local019] self_refine_start | branch=main, max_iter=1
[2026-04-29 15:46:02] [1/1] [local019] task_done | elapsed=232s
```

### 3.1 当前 retry 规则

会重试的情况：

- `429 rate limit`
- `max organization concurrency`
- 超时
- 临时网络故障
- `502/503/504`

不会重试的情况：

- `insufficient balance`
- `exceeded_current_quota`
- `suspended`
- `invalid temperature`
- `model not found`
- 鉴权失败

也就是说，当前逻辑已经区分：

- 临时性错误：等几秒再试
- 永久性错误：直接失败，不空耗时间

## 4. 如何扩充不同的 API 来源

当前扩展入口主要在：

- [chat.py](/Users/ying/Documents/老凤/text2sql/ReForce/ReFoRCE/methods/ReFoRCE/chat.py)

核心类是：

- `GPTChat`

### 4.1 现有支持方式

现在 `GPTChat` 已经支持几类来源：

1. `LLM_PROVIDER=moonshot`
   - 默认走 `https://api.moonshot.ai/v1`
   - 使用 `.env` 中的 `MOONSHOT_BASE_URL` / `MOONSHOT_API_KEY`
   - 常用模型包括：`kimi-k2.6`、`moonshot-v1-128k`、`moonshot-v1-32k`
   - `kimi-k2.6` 非思考模式建议 `temperature=0.6`，思考模式建议 `temperature=1`
   - `kimi-k2.6` 在思考模式下默认走流式调用

2. `LLM_PROVIDER=simpleai`
   - 默认走 `https://key.simpleai.com.cn/v1`
   - 使用 `.env` 中的 `SIMPLEAI_BASE_URL` / `SIMPLEAI_API_KEY`
   - 当前可直接尝试的模型包括：`claude-opus-4-6`、`claude-opus-4-7`、`claude-sonnet-4-6`、`claude-haiku-4-5-20251001`

3. `LLM_PROVIDER=openai`
   - 使用 `.env` 中的 `OPENAI_BASE_URL` / `OPENAI_API_KEY`

4. `LLM_PROVIDER=openai_compatible`
   - 使用 `.env` 中的 `OPENAI_COMPATIBLE_BASE_URL` / `OPENAI_COMPATIBLE_API_KEY`
   - 适合 OpenAI-compatible API 网关

5. `LLM_PROVIDER=local`
   - 使用 `.env` 中的 `LOCAL_BASE_URL` / `LOCAL_API_KEY`
   - 适合本地部署、OpenAI-compatible 接口

### 4.2 如果要扩新 provider，改哪里

如果你现在要再新增一个 provider，先判断它是不是 OpenAI-compatible：

- 如果兼容 OpenAI `chat.completions.create`，优先沿用现有主链路，只补 provider 路由和必要的响应清洗。
- 如果不兼容，再单独加请求格式适配。

最主要改这几个位置：

1. [chat.py](/Users/ying/Documents/老凤/text2sql/ReForce/ReFoRCE/methods/ReFoRCE/chat.py) 里的 `resolve_provider()`
   - 在这里新增 provider 名称和对应的：
     - `base_url`
     - `api_key`

2. 同文件的 `get_response()`
   - 如果新 provider 仍然兼容 OpenAI chat/completions 协议，通常不用大改
   - 如果协议不同，就在这里分支处理

3. 同文件的 `get_http_response()`
   - 如果你要支持一个不依赖 `openai` SDK、但 HTTP 协议又略有不同的服务，可以在这里扩展 payload 和返回解析

4. [config.env](/Users/ying/Documents/老凤/text2sql/ReForce/ReFoRCE/methods/ReFoRCE/config.env)
   - 给出对应的 `LLM_PROVIDER`
   - 配置默认模型、温度、thinking 支持情况等

### 4.3 两种扩展路径

#### A. 新来源兼容 OpenAI API

这是最简单的情况。

只需要在 `.env` 或环境变量里配置：

```bash
LLM_PROVIDER=openai_compatible
OPENAI_COMPATIBLE_BASE_URL=https://your-host/v1
OPENAI_COMPATIBLE_API_KEY=your-key
LLM_MODEL=your-model
```

这种情况下，往往不用再改 Python 代码。

#### B. 新来源不兼容 OpenAI API

这时建议：

1. 在 [chat.py](/Users/ying/Documents/老凤/text2sql/ReForce/ReFoRCE/methods/ReFoRCE/chat.py) 里新增一个 provider 分支
2. 明确这个 provider 的：
   - 请求 URL
   - 请求体格式
   - thinking 开关字段
   - max tokens 字段
   - 返回体提取逻辑
3. 复用现有的：
   - retry 机制
   - debug/test mode
   - response block 清洗逻辑

建议尽量让新 provider 仍然产出统一的字符串响应，这样：

- `extract_response_blocks()`
- `get_model_response()`

这些后续逻辑都不用动。

### 4.4 一个新 provider 的最小改法

如果你要接一个叫 `myvendor` 的新来源，通常流程是：

1. 在 `config.env` 里写：

```bash
LLM_PROVIDER=myvendor
LLM_MODEL=my-model
```

2. 在 `.env` 里写：

```bash
MYVENDOR_BASE_URL=https://api.myvendor.com/v1
MYVENDOR_API_KEY=your-key
```

3. 在 `resolve_provider()` 里新增：

```python
elif provider == "myvendor":
    base_url = os.environ.get("MYVENDOR_BASE_URL") or "https://api.myvendor.com/v1"
    api_key = os.environ.get("MYVENDOR_API_KEY")
```

4. 如果它其实完全兼容 OpenAI，而且你也不需要特殊清洗，其实还可以不新增 provider，直接用：

```bash
LLM_PROVIDER=openai_compatible
LLM_BASE_URL=https://api.myvendor.com/v1
LLM_API_KEY=your-key
LLM_MODEL=my-model
```

5. 如果协议兼容 OpenAI，就结束了  
   如果不兼容，再在 `get_http_response()` 或 `get_response()` 里加分支。

## 5. 当前推荐理解

如果只想先稳定跑起来，建议优先走：

- `moonshot-v1-128k`
- `THINK_OR_NOT=false`
- `NUM_WORKERS=1`
- `MAX_ITER=1`
- 小规模 `TASK_LIMIT`

如果要做更强实验，再逐步打开：

- `MAX_ITER=3`
- `DO_VOTE=true`
- `NUM_VOTES=3`
- `RANDOM_VOTE_FOR_TIE=true`
- `FINAL_CHOOSE=true`

这套配置更接近论文方法，但也更容易碰到 API 并发和额度问题。
