#!/bin/zsh
# Step 4: SPEED-ONLY re-run of the first ten models under the quiet box (quality already valid).
# Serial discipline: transfer XOR compute. Local incumbents benched in place; telesto models
# pulled one-at-a-time -> bench -> deleted. Resumable via done-markers. Heartbeats during pulls
# so an idle-reaper can't stall it. Writes canonical results/<label>.bench (overwrites contaminated).
set -u
BIN=$HOME/source/repos/llama.cpp/build/bin
REPO=$HOME/source/repos/MacminiM2Pro_ModelShowdown
RES=$REPO/results
DONE=$HOME/showdown-scratch/rerun-done; mkdir -p "$DONE"
TMP=$HOME/models/rerun-tmp

bench(){  # label gguf
  local L=$1 G=$2
  echo "@@@ $(date +%T) SPEED-START $L"
  pkill -f llama-server 2>/dev/null; sleep 1
  "$BIN/llama-bench" -m "$G" -ngl 99 -p 512 -n 128 -r 3 2>/dev/null | grep -E "pp512|tg128" > "$RES/$L.bench"
  touch "$DONE/$L"
  echo "@@@ $(date +%T) SPEED-DONE $L [$(tr '\n' ' ' < "$RES/$L.bench")]"
}

local_bench(){  # label gguf  (GGUF exists only on the Mac — keep it)
  local L=$1 G=$2
  [ -f "$DONE/$L" ] && { echo "skip $L (done)"; return; }
  bench "$L" "$G"
}

pull_bench(){  # label remote-relpath filename
  local L=$1 P=$2 F=$3
  [ -f "$DONE/$L" ] && { echo "skip $L (done)"; return; }
  rm -rf "$TMP"; mkdir -p "$TMP"
  echo "@@@ $(date +%T) PULL $L ($F)"
  rsync -a "akclark@telesto:$P/$F" "$TMP/" &
  local rp=$!
  while kill -0 $rp 2>/dev/null; do
    echo "  .. pulling $L: $(du -sm "$TMP" 2>/dev/null | cut -f1)MB $(date +%T)"
    sleep 30
  done
  wait $rp
  bench "$L" "$TMP/$F"
  rm -rf "$TMP"
}

# --- 3 local incumbents (bench in place, keep) ---
local_bench q35-9b-lcpp    "$HOME/models/q35-9b-gguf/Qwen_Qwen3.5-9B-Q4_K_M.gguf"
local_bench ornith-9b-lcpp "$HOME/models/ornith-1.0-9b-Q4_K_M.gguf"
local_bench dsc-lcpp       "$HOME/models/dsc-lite-gguf/DeepSeek-Coder-V2-Lite-Instruct-Q4_K_M.gguf"

# --- 7 pulled from telesto (pull -> bench -> delete) ---
pull_bench qwen25c-14b-lcpp  "models/q25c-14b-gguf"              "Qwen2.5-Coder-14B-Instruct-Q4_K_M.gguf"
pull_bench qwen25c-7b-lcpp   "models/q25c-7b-gguf"               "Qwen2.5-Coder-7B-Instruct-Q4_K_M.gguf"
pull_bench nemotron-9b-lcpp  "models/roster-stage/nemotron-9b-lcpp"  "nvidia_NVIDIA-Nemotron-Nano-9B-v2-Q4_K_M.gguf"
pull_bench phi4-lcpp         "models/roster-stage/phi4-lcpp"         "phi-4-Q4_K_M.gguf"
pull_bench gemma4-12b-lcpp   "models/roster-stage/gemma4-12b-lcpp"   "gemma-4-12B-it-Q4_K_M.gguf"
pull_bench granite-8b-lcpp   "models/roster-stage/granite-8b-lcpp"   "ibm-granite_granite-3.3-8b-instruct-Q4_K_M.gguf"
pull_bench codegemma-7b-lcpp "models/roster-stage/codegemma-7b-lcpp" "codegemma-7b-it-Q4_K_M.gguf"

echo "@@@ $(date +%T) RERUN_SPEED_ALL_DONE"
