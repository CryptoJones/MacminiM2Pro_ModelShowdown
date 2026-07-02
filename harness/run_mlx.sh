#!/bin/zsh
# MLX side of the matrix: for each model, MLX speed (mlx_lm.generate) + MLX quality
# (mlx_lm.server + EvalPlus). Serial (transfer XOR compute), quiet box, resumable, heartbeats.
# Result naming matches update_readme.py: <label>@MLX.speed (tgm), <label>-mlx.evalplus (hm).
# NOTE: mlx_lm.server routes by the request "model" field, so EvalPlus is given the model DIR path.
set -u
VENV=$HOME/.venvs/showdown-evalplus
PY=$VENV/bin/python
REPO=$HOME/source/repos/MacminiM2Pro_ModelShowdown
RES=$REPO/results
SCR=$HOME/showdown-scratch; MRES=$SCR/results
DONE=$SCR/mlx-done; mkdir -p "$DONE" "$MRES"
TMP=$HOME/models/mlx-rerun-tmp
PORT=8081
export OPENAI_API_KEY=dummy
PROMPT="Write a Python function that returns the nth Fibonacci number."

mlx_speed(){  # label dir
  local L=$1 D=$2
  pkill -f "mlx_lm.server|llama-server" 2>/dev/null; sleep 1
  echo "@@@ $(date +%T) MLX-SPEED $L"
  $PY -m mlx_lm generate --model "$D" --prompt "$PROMPT" --max-tokens 128 2>&1 \
    | grep -iE "Prompt:|Generation:|Peak memory:" > "$RES/$L@MLX.speed"
}
mlx_quality(){  # label dir
  local L=$1 D=$2
  echo "@@@ $(date +%T) MLX-QUALITY $L"
  pkill -f "mlx_lm.server|llama-server" 2>/dev/null; sleep 1
  $PY -m mlx_lm.server --model "$D" --host 127.0.0.1 --port $PORT > "$MRES/$L.mlxserver.log" 2>&1 &
  for i in $(seq 1 180); do curl -s -m2 http://127.0.0.1:$PORT/v1/models >/dev/null 2>&1 && { echo "server ready ${i}s"; break; }; sleep 1; done
  local ROOT=$SCR/eval/mlx_$L
  $PY -m evalplus.codegen "$D" humaneval --backend openai \
    --base_url "http://127.0.0.1:$PORT/v1" --greedy --root "$ROOT" > "$MRES/$L.mlx.codegen.log" 2>&1
  local J=$(find "$ROOT" -name "*temp_0.0.jsonl" ! -name "*.raw.jsonl" | head -1)
  rm -f "$ROOT"/humaneval/*_eval_results.json 2>/dev/null
  $PY -m evalplus.evaluate humaneval --samples "$J" 2>&1 | grep -iE "pass@1|humaneval" | tee "$RES/$L-mlx.evalplus"
  pkill -f mlx_lm.server 2>/dev/null; sleep 1
}
finish(){  # label
  local L=$1
  touch "$DONE/$L"
  echo "@@@ $(date +%T) MLX-DONE $L speed[$(grep -i Generation "$RES/$L@MLX.speed" 2>/dev/null)] qual[$(tr '\n' ' ' < "$RES/$L-mlx.evalplus" 2>/dev/null)]"
}
run_local(){  # label dir
  local L=$1 D=$2
  [ -f "$DONE/$L" ] && { echo "skip $L (done)"; return; }
  mlx_speed "$L" "$D"; mlx_quality "$L" "$D"; finish "$L"
}
run_pull(){  # label stagedir
  local L=$1 S=$2
  [ -f "$DONE/$L" ] && { echo "skip $L (done)"; return; }
  rm -rf "$TMP"; mkdir -p "$TMP"
  echo "@@@ $(date +%T) MLX-PULL $L (mlx-stage/$S)"
  rsync -a "akclark@telesto:models/mlx-stage/$S/" "$TMP/" &
  local rp=$!
  while kill -0 $rp 2>/dev/null; do echo "  .. pull $L $(du -sm "$TMP" 2>/dev/null | cut -f1)MB $(date +%T)"; sleep 30; done
  wait $rp
  mlx_speed "$L" "$TMP"; mlx_quality "$L" "$TMP"; finish "$L"
  rm -rf "$TMP"
}

run_local  ornith-9b   "$HOME/models/ornith-9b-mlx-4bit"
run_pull   qwen25c-7b  qwen25c-7b
run_pull   q35-9b      q35-9b-lcpp
run_pull   granite-8b  granite-8b-lcpp
run_pull   codegemma-7b codegemma-7b-lcpp
run_pull   nemotron-9b nemotron-9b-lcpp
run_pull   dsc         dsc-lcpp
run_pull   gemmacoder  gemmacoder-lcpp
run_pull   gemma4-12b  gemma4-12b-lcpp
run_pull   qwen25c-14b qwen25c-14b
run_pull   phi4        phi4-lcpp
run_pull   gptoss-20b  gptoss-20b-lcpp
echo "@@@ $(date +%T) MLX_ALL_DONE"
