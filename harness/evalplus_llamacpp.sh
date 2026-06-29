#!/bin/zsh
# Full EvalPlus HumanEval+ for one GGUF on the fixed llama.cpp binary.
# usage: evalplus_llamacpp.sh <gguf> <label>
BIN=/Users/akclark/source/repos/llama.cpp/build/bin
SCRATCH=/private/tmp/claude-501/-Users-akclark-source-repos-llama-cpp/9f7c5ac9-63a7-42e8-93e1-97c56db68a55/scratchpad
V="$SCRATCH/evalplus-venv/bin"
GGUF=$1; LABEL=$2
PORT=8081
RES=$SCRATCH/eval/results; ROOT=$SCRATCH/eval/ep_$LABEL
mkdir -p $ROOT $RES
export OPENAI_API_KEY=dummy

echo "### binary:"; $BIN/llama-cli --version 2>&1 | grep -i version | head -1
echo "### start llama-server ($LABEL)"
$BIN/llama-server -m "$GGUF" -ngl 99 -c 4096 --host 127.0.0.1 --port $PORT --jinja > $RES/$LABEL.epserver.log 2>&1 &
SV=$!
for i in $(seq 1 60); do curl -s -m 2 http://127.0.0.1:$PORT/health 2>/dev/null | grep -q '"ok"' && { echo "ready ${i}s"; break; }; sleep 1; done

echo "### codegen humaneval (full 164, greedy)"
"$V/python" -m evalplus.codegen local humaneval --backend openai --base_url "http://127.0.0.1:$PORT/v1" --greedy --root "$ROOT" 2>&1 | tail -3
JSONL=$(find "$ROOT" -name "*temp_0.0.jsonl" ! -name "*.raw.jsonl" | head -1)
echo "### samples: $JSONL"
echo "### evaluate"
"$V/python" -m evalplus.evaluate humaneval --samples "$JSONL" 2>&1 | grep -iE "pass@1|humaneval" | tee $RES/$LABEL.evalplus
kill $SV 2>/dev/null || true; sleep 2
echo "### DONE $LABEL"
