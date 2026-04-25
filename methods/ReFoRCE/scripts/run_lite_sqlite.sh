#!/bin/bash
set -e

load_env_defaults() {
  local file="$1"
  [ -f "$file" ] || return 0
  while IFS='=' read -r key value; do
    key="${key#"${key%%[![:space:]]*}"}"
    key="${key%"${key##*[![:space:]]}"}"
    value="${value#"${value%%[![:space:]]*}"}"
    value="${value%"${value##*[![:space:]]}"}"
    if [ -z "$key" ] || [[ "$key" == \#* ]]; then
      continue
    fi
    if [ -z "${!key+x}" ]; then
      export "$key=$value"
    fi
  done < "$file"
}

load_env_defaults .env
load_env_defaults config.env
PYTHON_BIN=${PYTHON_BIN:-python3}

MODEL=${1:-${LLM_MODEL:-kimi-k2.6}}
OUTPUT_PATH=${OUTPUT_PATH:-output/${MODEL}-lite-sqlite-log}
NUM_WORKERS=${NUM_WORKERS:-4}
MAX_ITER=${MAX_ITER:-3}
TEMPERATURE=${LLM_TEMPERATURE:-1}
TASK_LIMIT=${TASK_LIMIT:-0}
TASK_OFFSET=${TASK_OFFSET:-0}
ADD_TIMESTAMP=${ADD_TIMESTAMP:-true}
SQLITE_DIR="../../spider2-lite/resource/databases/spider2-localdb"

if [ "$MODEL" = "moonshot-v1-128k" ]; then
  export THINK_OR_NOT=false
fi

if [ "$ADD_TIMESTAMP" = "true" ] || [ "$ADD_TIMESTAMP" = "1" ] || [ "$ADD_TIMESTAMP" = "yes" ]; then
  TIMESTAMP=$(date +"%Y%m%d-%H%M%S")
  OUTPUT_PATH="${OUTPUT_PATH}-${TIMESTAMP}"
fi

if [ ! -d "$SQLITE_DIR" ] || ! find "$SQLITE_DIR" -name "*.sqlite" -print -quit | grep -q .; then
  echo "Missing Spider2-Lite SQLite databases under $SQLITE_DIR"
  echo "The repository includes SQLite schema JSON files, but not the executable .sqlite databases."
  echo "Run the Lite SQLite database download step first, then rerun this script."
  echo "Original ReFoRCE command that downloads them: bash scripts/run_main.sh --task lite --model $MODEL"
  exit 1
fi

"$PYTHON_BIN" run.py \
    --task lite \
    --subtask sqlite \
    --do_self_refinement \
    --generation_model "$MODEL" \
    --max_iter "$MAX_ITER" \
    --temperature "$TEMPERATURE" \
    --early_stop \
    --omnisql_format_pth ../../data/omnisql_spider2_sqlite.json \
    --output_path "$OUTPUT_PATH" \
    --num_workers "$NUM_WORKERS" \
    --limit_tasks "$TASK_LIMIT" \
    --task_offset "$TASK_OFFSET" \
    --overwrite_unfinished
