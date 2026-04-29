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
UPDATE=false
while [[ $# -gt 0 ]]; do
  key="$1"
  case $key in
    --update)
      UPDATE=true
      shift # past argument
      ;;
    --task)
      TASK="$2"
      shift
      shift
      ;;
    --log_folder)
      LOG_FOLDER="$2"
      shift
      shift
      ;;
    *)
      shift
      ;;
  esac
done
CMD1="\"$PYTHON_BIN\" eval.py --log_folder $LOG_FOLDER --task $TASK"
if [ "$UPDATE" = true ]; then
  CMD1="$CMD1 --update_res"
fi

eval $CMD1
