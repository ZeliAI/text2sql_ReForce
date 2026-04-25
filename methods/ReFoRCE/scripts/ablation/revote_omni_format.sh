#!/bin/bash
set -e
PYTHON_BIN=${PYTHON_BIN:-python3}
while [[ $# -gt 0 ]]; do
  key="$1"
  case $key in
    --task)
      TASK="$2"
      shift
      shift
      ;;
    --output_path)
      OUTPUT_PATH="$2"
      shift
      shift
      ;;
    *)
      shift
      ;;
  esac
done
"$PYTHON_BIN" run.py \
    --task $TASK \
    --db_path examples_${TASK} \
    --output_path $OUTPUT_PATH \
    --revote \
    --do_vote \
    --random_vote_for_tie \
    --final_choose \
    --num_votes 8 \
    --num_workers 1 \
    --omnisql_format_pth ../../data/omnisql_spider2_sqlite.json
eval $CMD1
"$PYTHON_BIN" eval.py --log_folder $OUTPUT_PATH --task $TASK