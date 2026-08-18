#!/bin/zsh
# Archive a completed EvalPlus run INTO THE REPO so nothing must be reconstructed later.
#
# WHY THIS EXISTS: scratch gets wiped. Before this, raw generations survived for only 2 of 15
# models, which made most of the matrix un-auditable and cost a whole investigation (issue #7).
# This copies the samples AND records the invocation parameters next to them.
#
# Usage: archive_run.sh <label> <lcpp|mlx> <evalplus-root> [model-path] [server-cmd]
set -u
LABEL=$1; RUNTIME=$2; ROOT=$3; MODEL=${4:-}; SERVERCMD=${5:-}
REPO=$HOME/source/repos/MacminiM2Pro_ModelShowdown
ID="$LABEL"; [ "$RUNTIME" = "mlx" ] && ID="$LABEL-mlx"
DEST="$REPO/results/raw/$ID"; mkdir -p "$DEST" "$REPO/results/runs"

find "$ROOT" \( -name "*temp_0.0*.jsonl" -o -name "*_eval_results.json" \) 2>/dev/null \
  | while read -r f; do cp -f "$f" "$DEST/" 2>/dev/null; done

RAW=$(find "$DEST" -name "*.raw.jsonl" | head -1)

# An EMPTY response is not a wrong answer. Counting them is the point (issue #7).
COUNTS=$(RAWP="$RAW" python3 -c '
import json,os
p=os.environ.get("RAWP","")
if not p or not os.path.exists(p): print("0 0")
else:
    rows=[json.loads(l) for l in open(p) if l.strip()]
    print(len(rows), sum(1 for r in rows if not (r.get("solution") or "").strip()))
')
TOTAL=${COUNTS%% *}; EMPTY=${COUNTS##* }
echo "$EMPTY" > "$REPO/results/$ID.empties"

MSIZE=""; MSHA=""
if [ -n "$MODEL" ] && [ -f "$MODEL" ]; then
  MSIZE=$(stat -f%z "$MODEL"); MSHA=$(shasum -a 256 "$MODEL" | cut -d' ' -f1)
fi
IDLE=$(top -l 2 -n 0 2>/dev/null | grep "^CPU usage" | tail -1 | sed -n 's/.*, \([0-9.]*\)% idle.*/\1/p')
HGIT=$(git -C "$REPO" rev-parse --short HEAD 2>/dev/null)

ID="$ID" LABEL="$LABEL" RUNTIME="$RUNTIME" MODEL="$MODEL" MSIZE="$MSIZE" MSHA="$MSHA" \
SERVERCMD="$SERVERCMD" TOTAL="$TOTAL" EMPTY="$EMPTY" IDLE="$IDLE" HGIT="$HGIT" \
OUT="$REPO/results/runs/$ID.json" python3 -c '
import json,os,platform,datetime
g=os.environ.get
def num(x,f=float):
    try: return f(x)
    except Exception: return None
json.dump({
 "run_id": g("ID"), "label": g("LABEL"), "runtime": g("RUNTIME"),
 "recorded_at": datetime.datetime.now().astimezone().isoformat(),
 "provenance": {
   "harness_script": "harness/run_quality.sh" if g("RUNTIME")=="lcpp" else "harness/run_mlx.sh",
   "harness_git_commit": g("HGIT"),
   "server_cmd": g("SERVERCMD"),
   "evalplus_cmd": "python -m evalplus.codegen <model> humaneval --backend openai --base_url http://127.0.0.1:8081/v1 --greedy",
   "max_new_tokens": 4096,
   "max_new_tokens_source": "evalplus/provider/base.py (applies to BOTH runtimes)"
 },
 "model": {"path": g("MODEL") or None, "size_bytes": num(g("MSIZE"),int), "sha256": g("MSHA") or None},
 "environment": {"host": platform.node(), "machine": platform.machine(),
                 "os": platform.mac_ver()[0], "cpu_idle_pct_at_archive": num(g("IDLE"))},
 "results": {"total_tasks": num(g("TOTAL"),int), "empty_completions": num(g("EMPTY"),int)}
}, open(g("OUT"),"w"), indent=2)
print("manifest ->", g("OUT"))
'
echo "@@@ ARCHIVED $ID: $EMPTY/$TOTAL empty -> results/raw/$ID/"
