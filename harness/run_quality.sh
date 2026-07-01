#!/bin/zsh
# Persistent-path EvalPlus HumanEval+ quality runner for one GGUF.
# Survives reboot (venv + scratch live outside /private/tmp). Usage: run_quality.sh <label> <gguf>
# Serial-discipline: assumes NO transfer in flight; starts its own llama-server and kills it after.
set -u
LABEL=$1; GGUF=$2
BIN=$HOME/source/repos/llama.cpp/build/bin
VENV=$HOME/.venvs/showdown-evalplus
REPO=$HOME/source/repos/MacminiM2Pro_ModelShowdown
SCR=$HOME/showdown-scratch; RES=$SCR/results; ROOT=$SCR/eval/ep_$LABEL
mkdir -p "$ROOT" "$RES"
export OPENAI_API_KEY=dummy
PORT=8081
echo "@@@ $(date +%T) QUALITY-START $LABEL"
pkill -f llama-server 2>/dev/null; sleep 2
"$BIN/llama-server" -m "$GGUF" -ngl 99 -c 4096 --host 127.0.0.1 --port $PORT --jinja > "$RES/$LABEL.qserver.log" 2>&1 &
for i in $(seq 1 180); do
  curl -s -m2 http://127.0.0.1:$PORT/health 2>/dev/null | grep -q '"ok"' && { echo "server ready ${i}s"; break; }
  sleep 1
done
"$VENV/bin/python" -m evalplus.codegen local humaneval --backend openai \
  --base_url "http://127.0.0.1:$PORT/v1" --greedy --root "$ROOT" > "$RES/$LABEL.codegen.log" 2>&1
J=$(find "$ROOT" -name "*temp_0.0.jsonl" ! -name "*.raw.jsonl" | head -1)
echo "samples: $J"
rm -f "$ROOT"/humaneval/*_eval_results.json 2>/dev/null
"$VENV/bin/python" -m evalplus.evaluate humaneval --samples "$J" 2>&1 \
  | grep -iE "pass@1|humaneval" | tee "$REPO/results/$LABEL.evalplus"
pkill -f llama-server 2>/dev/null; sleep 2
echo "@@@ $(date +%T) QUALITY-DONE $LABEL -> $(tr '\n' ' ' < "$REPO/results/$LABEL.evalplus")"
