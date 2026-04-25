# Local Text-to-SQL Agent Smoke Test

This repo's original `run_main.sh --task lite` downloads Spider2 SQLite databases with `gdown`.
For local debugging without external DB downloads or embeddings, use the stdlib-only smoke test:

```bash
cd methods/ReFoRCE
source scripts/use_python3.sh
python3 -B run_local_demo.py --mock
```

It creates a tiny SQLite database at `examples_local/local_demo/demo.sqlite`, runs a Text-to-SQL loop, and writes:

- `output/local-demo/result.sql`
- `output/local-demo/result.csv`
- `output/local-demo/log.json`

To call an OpenAI-compatible LLM endpoint:

```bash
export LLM_BASE_URL="https://your-host/v1"
export LLM_API_KEY="your-api-key"
export LLM_MODEL="your-model"
python3 -B run_local_demo.py --model "$LLM_MODEL"
```

For Moonshot/Kimi `kimi-k2.6`, keep temperature at `1`:

```bash
export LLM_BASE_URL="https://api.moonshot.ai/v1"
export LLM_MODEL="kimi-k2.6"
python3 -B run_local_demo.py --model "$LLM_MODEL" --temperature 1
```

You can also point it at your own SQLite file:

```bash
python3 -B run_local_demo.py \
  --sqlite /path/to/your.db \
  --question "your natural language question" \
  --model "$LLM_MODEL"
```

Schema retrieval is intentionally simple: tables are ranked by keyword overlap between the question and table/column names.

The local `.env` file is automatically loaded by `chat.py`, so you can also keep these values in:

```bash
methods/ReFoRCE/.env
```

## Spider2-Lite SQLite Only

For your Lite-only workflow, skip Snowflake and use the SQLite runner:

```bash
cd methods/ReFoRCE
source scripts/use_python3.sh
export LLM_API_KEY="your-api-key"
bash scripts/run_lite_sqlite.sh kimi-k2.6
```

This uses `data/omnisql_spider2_sqlite.json` and `--subtask sqlite`. It does not touch Snowflake.
It still needs executable Spider2-Lite `.sqlite` files under `spider2-lite/resource/databases/spider2-localdb`,
which are not included in this clone; the checked-in `spider2-lite/resource/databases/sqlite` folder contains schema JSON files.

Lite runs are controlled by `methods/ReFoRCE/config.env`:

```bash
LLM_MODEL=kimi-k2.6
LLM_TEMPERATURE=0.6
LLM_MAX_TOKENS=4096
THINK_OR_NOT=false
NUM_WORKERS=1
MAX_ITER=1
TASK_LIMIT=3
TASK_OFFSET=10
OUTPUT_PATH=output/kimi-k2.6-lite-sqlite-3tasks-offset10-no-thinking
ADD_TIMESTAMP=true
```

`THINK_OR_NOT=false` sends `extra_body={"thinking": {"type": "disabled"}}` for OpenAI-compatible chat calls.
Supported model examples are `kimi-k2.6` and `moonshot-v1-128k`; `moonshot-v1-128k` does not support thinking mode.
When `ADD_TIMESTAMP=true`, the runner appends `YYYYMMDD-HHMMSS` to the output directory.
