#!/bin/bash
set -e

load_env_defaults() {
  local file="$1"
  [ -f "$file" ] || return 0
  while IFS='=' read -r key value; do
    key="${key#"${key%%[![:space:]]*}"}"
    key="${key%"${key##*[![:space:]]}"}"
    value="${value%%[[:space:]]#*}"
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
NUM_WORKERS=${NUM_WORKERS:-4}
MAX_ITER=${MAX_ITER:-3}
TEMPERATURE=${LLM_TEMPERATURE:-1}
TASK_LIMIT=${TASK_LIMIT:-0}
TASK_OFFSET=${TASK_OFFSET:-0}
DO_VOTE=${DO_VOTE:-false}
NUM_VOTES=${NUM_VOTES:-3}
RANDOM_VOTE_FOR_TIE=${RANDOM_VOTE_FOR_TIE:-false}
FINAL_CHOOSE=${FINAL_CHOOSE:-false}
ADD_TIMESTAMP=${ADD_TIMESTAMP:-true}
DO_SCHEMA_SUMMARY=${DO_SCHEMA_SUMMARY:-true}
SCHEMA_SUMMARY_MODEL=${SCHEMA_SUMMARY_MODEL:-$MODEL}
SELECTOR_MODEL=${SELECTOR_MODEL:-$MODEL}
SQLITE_DIR="../../spider2-lite/resource/databases/spider2-localdb"

if [ "$MODEL" = "moonshot-v1-128k" ] || [ "$MODEL" = "moonshot-v1-64k" ]; then
  export THINK_OR_NOT=false
fi

if [ -z "${OUTPUT_PATH:-}" ]; then
  THINKING_LABEL="no-thinking"
  if [ "${THINK_OR_NOT:-false}" = "true" ] || [ "${THINK_OR_NOT:-false}" = "1" ] || [ "${THINK_OR_NOT:-false}" = "yes" ]; then
    THINKING_LABEL="thinking"
  fi
  OUTPUT_PATH="output/${MODEL}-lite-sqlite-${THINKING_LABEL}-limit${TASK_LIMIT}-offset${TASK_OFFSET}"
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

EXTRA_ARGS=()
if [ "$DO_VOTE" = "true" ] || [ "$DO_VOTE" = "1" ] || [ "$DO_VOTE" = "yes" ]; then
  EXTRA_ARGS+=(--do_vote --num_votes "$NUM_VOTES")
fi

if [ "$RANDOM_VOTE_FOR_TIE" = "true" ] || [ "$RANDOM_VOTE_FOR_TIE" = "1" ] || [ "$RANDOM_VOTE_FOR_TIE" = "yes" ]; then
  EXTRA_ARGS+=(--random_vote_for_tie)
fi

if [ "$FINAL_CHOOSE" = "true" ] || [ "$FINAL_CHOOSE" = "1" ] || [ "$FINAL_CHOOSE" = "yes" ]; then
  EXTRA_ARGS+=(--final_choose --selector_model "$SELECTOR_MODEL")
fi

if [ "$DO_SCHEMA_SUMMARY" = "true" ] || [ "$DO_SCHEMA_SUMMARY" = "1" ] || [ "$DO_SCHEMA_SUMMARY" = "yes" ]; then
  EXTRA_ARGS+=(--do_schema_summary --schema_summary_model "$SCHEMA_SUMMARY_MODEL")
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
    --overwrite_unfinished \
    "${EXTRA_ARGS[@]}"
