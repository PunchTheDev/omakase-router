#!/usr/bin/env bash
# Self-score the current submission/ against the dev split — the same judgment
# the maintainer's canonical rerun applies. Boots a throwaway mock pool.
set -euo pipefail
cd "$(dirname "$0")/.."
EVAL=../oc-eval
PY=$EVAL/.venv/bin/python
[ -x "$PY" ] || PY=python3

$PY -m oc_eval.cli mockpool --port 8100 & POOL_PID=$!
trap 'kill $POOL_PID 2>/dev/null' EXIT
sleep 0.3

mkdir -p runs
[ -f runs/baselines.dev.json ] || \
  $PY -m oc_eval.cli baselines --pool $EVAL/configs/pool.dev.json --split dev --seed 1 --out runs/baselines.dev.json

$PY -m oc_eval.cli run \
  --manifest submission/manifest.json \
  --pool $EVAL/configs/pool.dev.json \
  --baselines runs/baselines.dev.json \
  --split dev --seed 1 "$@"
