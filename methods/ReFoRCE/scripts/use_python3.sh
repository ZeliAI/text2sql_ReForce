#!/bin/bash

# Source this file from methods/ReFoRCE to make local commands prefer Python 3:
#   source scripts/use_python3.sh

export PYTHON_BIN="${PYTHON_BIN:-python3}"
export LLM_BASE_URL="${LLM_BASE_URL:-https://api.moonshot.ai/v1}"
export LLM_MODEL="${LLM_MODEL:-kimi-k2.6}"

if [ -f .env ]; then
  set -a
  source .env
  set +a
fi

alias python=python3
