#!/bin/zsh
# SINGLE serial master. INVARIANT: the Mac is EITHER transferring OR evaluating, never both.
# Transfers (pull from telesto / archive to telesto) only happen with NO llama-server running.
# telesto staging runs independently on telesto (not the Mac), which is allowed.
BIN=/Users/akclark/source/repos/llama.cpp/build/bin
SCRATCH=/private/tmp/claude-501/-Users-akclark-source-repos-llama-cpp/9f7c5ac9-63a7-42e8-93e1-97c56db68a55/scratchpad
V="$SCRATCH/evalplus-venv/bin"; R=$SCRATCH/eval/results; M=/Users/akclark/models
export OPENAI_API_KEY=dummy; PORT=8081

eval_model(){  # label gguf   (COMPUTE phase: server + bench + codegen + evaluate; no transfers)
  local LABEL=$1 GGUF=$2
  echo "@@@ $(date +%T) EVAL-START $LABEL"
  pkill -f llama-server 2>/dev/null; sleep 2
  $BIN/llama-server -m "$GGUF" -ngl 99 -c 4096 --host 127.0.0.1 --port $PORT --jinja > $R/$LABEL.srv.log 2>&1 &
  local SV=$!
  for i in $(seq 1 120); do curl -s -m2 http://127.0.0.1:$PORT/health 2>/dev/null|grep -q '"ok"' && break; sleep 1; done
  $BIN/llama-bench -m "$GGUF" -ngl 99 -p 512 -n 128 -r 3 2>/dev/null | grep -E "pp512|tg128" > $R/$LABEL.bench
  local ROOT=$SCRATCH/eval/ep_$LABEL
  "$V/python" -m evalplus.codegen local humaneval --backend openai --base_url http://127.0.0.1:$PORT/v1 --greedy --root "$ROOT" --resume > $R/$LABEL.codegen.log 2>&1
  local J=$(find "$ROOT" -name "*temp_0.0.jsonl" ! -name "*.raw.jsonl"|head -1)
  rm -f "$ROOT"/humaneval/*_eval_results.json
  "$V/python" -m evalplus.evaluate humaneval --samples "$J" 2>&1 | grep -iE pass@1 | tr '\n' ' ' > $R/$LABEL.evalplus
  pkill -f llama-server 2>/dev/null; sleep 2
  echo "@@@ $(date +%T) EVAL-DONE $LABEL bench[$(cat $R/$LABEL.bench|tr '\n' ' ')] eval[$(cat $R/$LABEL.evalplus)]"
}
archive(){  # dir-name  (TRANSFER phase: only call with NO server running)
  local d=$1; [ -d "$M/$d" ] || return
  echo "@@@ $(date +%T) ARCHIVE $d -> telesto"
  rsync -a "$M/$d" akclark@telesto:~/models/ > $R/arc-$d.log 2>&1
  local N=$(ssh akclark@telesto "ls ~/models/$d/* 2>/dev/null|wc -l|tr -d ' '")
  [ "$N" -ge 1 ] && { rm -rf "$M/$d"; echo "@@@ $d archived+removed"; } || echo "@@@ $d ARCHIVE FAILED"
}
pull(){  # label file  (TRANSFER phase: wait for telesto stage, pull over LAN; no server running)
  local L=$1 F=$2
  until ssh akclark@telesto "[ -f ~/models/roster-stage/$L/$F ]" 2>/dev/null; do sleep 30; done
  mkdir -p "$M/roster-$L"
  echo "@@@ $(date +%T) PULL $L from telesto"
  rsync -a "akclark@telesto:~/models/roster-stage/$L/$F" "$M/roster-$L/" > $R/$L.pull.log 2>&1
}

# --- TRANSFER window: free disk by archiving idle, already-evaluated locals (no server running) ---
archive q25c-14b-gguf
archive q25c-7b-mlx
archive q35-9b-mlx

# --- q35 (local), resume codegen + eval ---
eval_model q35-9b-lcpp "$M/q35-9b-gguf/Qwen_Qwen3.5-9B-Q4_K_M.gguf"

# --- DeepSeek: local copy was emptied; re-pull from telesto (transfer), then eval ---
rm -rf "$M/dsc-lite-gguf"; mkdir -p "$M/dsc-lite-gguf"
rsync -a "akclark@telesto:~/models/dsc-lite-gguf/" "$M/dsc-lite-gguf/" > $R/dsc.pull.log 2>&1
eval_model dsc-lcpp "$M/dsc-lite-gguf/DeepSeek-Coder-V2-Lite-Instruct-Q4_K_M.gguf"

# --- ornith (local incumbent) ---
eval_model ornith-9b-lcpp "$M/ornith-1.0-9b-Q4_K_M.gguf"

# --- roster: pull (transfer) then eval (compute), strictly serial ---
for e in \
 "nemotron-9b-lcpp:nvidia_NVIDIA-Nemotron-Nano-9B-v2-Q4_K_M.gguf" \
 "granite-8b-lcpp:ibm-granite_granite-3.3-8b-instruct-Q4_K_M.gguf" \
 "codegemma-7b-lcpp:codegemma-7b-it-Q4_K_M.gguf" \
 "gemma4-12b-lcpp:gemma-4-12B-it-Q4_K_M.gguf" \
 "phi4-lcpp:phi-4-Q4_K_M.gguf" \
 "gptoss-20b-lcpp:gpt-oss-20b-mxfp4.gguf" ; do
  L=${e%%:*}; F=${e#*:}
  pull "$L" "$F"
  eval_model "$L" "$M/roster-$L/$F"
  rm -rf "$M/roster-$L"   # telesto roster-stage/$L is the archive
done

# --- final archive of remaining locals (all evals done; transfers safe) ---
archive q35-9b-gguf
archive dsc-lite-gguf
echo "FINISH_ALL_DONE $(date +%T)"
