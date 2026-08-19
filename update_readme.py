#!/usr/bin/env python3
"""Regenerate README.md results table from results/*.evalplus / *.bench / *.speed."""
import os, glob, re, sys
HERE = os.path.dirname(os.path.abspath(__file__))
R = os.path.join(HERE, "results")
META = {  # canonical -> (vendor/gen, params)
 "Ternary-Bonsai-27B": ("Prism ML 2026 (Qwen3.6-based ternary)", "27B"),
 "Qwen3.5-9B": ("Alibaba 2026 (reasoning/MTP)", "9B"),
 "ornith-9B": ("DeepReinforce 2026 (Qwen3.5-based)", "9B"),
 "Qwen2.5-Coder-14B": ("Alibaba 2024 (dedicated coder)", "14B"),
 "Qwen2.5-Coder-7B": ("Alibaba 2024 (dedicated coder)", "7B"),
 "DeepSeek-V2-Lite": ("DeepSeek 2024 (MoE, 2.4B active)", "16B"),
 "NVIDIA-Nemotron-9B": ("NVIDIA 2026 (reasoning)", "9B"),
 "IBM-Granite-8B": ("IBM / Red Hat", "8B"),
 "Phi-4": ("Microsoft", "14B"),
 "Gemma-4-12B": ("Google 2026", "12B"),
 "CodeGemma-7B": ("Google 2024", "7B"),
 "gpt-oss-20b": ("OpenAI", "20B (MoE)"),
 "Gemma-4-12B-Coder": ("community finetune of Gemma-4-12B (fable5/composer2.5)", "12B"),
 "Qwythos-9B-v2": ("Empero AI 2026 (Qwen3.5-based reasoning finetune)", "9B"),
 "Qwen3.8-27B (UD-IQ2_M)": ("Alibaba 2026 (dense, multimodal, reasoning) - 2-bit budget-edge", "27B"),
}
NAME = {'q14b':'Qwen2.5-Coder-14B','qwen25c-14b':'Qwen2.5-Coder-14B','q7b':'Qwen2.5-Coder-7B','qwen25c-7b':'Qwen2.5-Coder-7B',
 'q35-9b':'Qwen3.5-9B','dsc':'DeepSeek-V2-Lite','dsc-lite':'DeepSeek-V2-Lite','ornith-9b':'ornith-9B',
 'nemotron-9b':'NVIDIA-Nemotron-9B','granite-8b':'IBM-Granite-8B','codegemma-7b':'CodeGemma-7B',
 'gemma4-12b':'Gemma-4-12B','phi4':'Phi-4','gptoss-20b':'gpt-oss-20b','gemmacoder':'Gemma-4-12B-Coder',
 'qwythos-v2':'Qwythos-9B-v2','ternary-bonsai-27b':'Ternary-Bonsai-27B',
 'qwen38-27b':'Qwen3.8-27B (UD-IQ2_M)'}
# Models that emit a <think> reasoning block before their answer. These are at risk of the
# reasoning-overrun defect: llama.cpp with --jinja splits reasoning out of `content`, so a model
# that never finishes thinking inside max_new_tokens returns EMPTY content and is scored wrong.
# Measured on Qwen3.8-27B: HumanEval/10 -> finish_reason=length, content=0 chars,
# reasoning_content=14451 chars, completion_tokens=4096.
REASONING = {
    "Qwen3.5-9B", "ornith-9B", "NVIDIA-Nemotron-9B", "Qwythos-9B-v2",
    "Ternary-Bonsai-27B", "Qwen3.8-27B (UD-IQ2_M)", "gpt-oss-20b",
}

def canon(s):
    mlx = s.endswith('-mlx'); s = s[:-4] if mlx else s
    s = s.replace('@llamacpp','').replace('-lcpp','').replace('@MLX','')
    return NAME.get(s, s), mlx
rows = {}
for f in glob.glob(R+"/*.evalplus"):
    nm, mlx = canon(os.path.basename(f)[:-9]); m = re.findall(r"pass@1:\s*([0-9.]+)", open(f).read())
    if len(m) >= 2: rows.setdefault(nm, {})[('hm' if mlx else 'hg')] = round(float(m[1])*100, 1)
for f in glob.glob(R+"/*.bench"):
    nm, _ = canon(os.path.basename(f)[:-6]); tg = re.search(r"tg128 *\| *([0-9.]+)", open(f).read())
    if tg: rows.setdefault(nm, {})['tgg'] = round(float(tg.group(1)))
# llama.cpp reports the NOMINAL file_type. Unsloth "UD-" dynamic quants misreport it:
# Qwen3.8-27B-UD-IQ2_M declares Q4_K_S but is ~2.8 bits/weight (9.60 GiB / 27.32 B).
# Override those explicitly rather than publishing the header's claim.
QUANT_OVERRIDE = {"Qwen3.8-27B (UD-IQ2_M)": "UD-IQ2_M"}
for f in glob.glob(R+"/*.bench"):
    nm, _ = canon(os.path.basename(f)[:-6])
    txt = open(f).read()
    m = re.search(r"\|\s*([^|]*?)\s*\|\s*([0-9.]+)\s*GiB", txt)
    if m:
        desc, size = m.group(1), m.group(2)
        qm = re.search(r"(Q\d[^|]*?|MXFP4[^|]*?|IQ\d[^|]*?|BF16|F16)\s*$", desc)
        q = qm.group(1).strip() if qm else "?"
        q = QUANT_OVERRIDE.get(nm, q)
        q = q.replace("Q4_K - Medium", "Q4_K_M").replace("Q4_K - Small", "Q4_K_S")
        rows.setdefault(nm, {})['qz'] = f"{q} · {size} GiB"
for f in glob.glob(R+"/*.empties"):
    nm, mlx = canon(os.path.basename(f)[:-8]); v = open(f).read().strip()
    if v.isdigit(): rows.setdefault(nm, {})[('em' if mlx else 'eg')] = int(v)
for f in glob.glob(R+"/*.speed"):
    nm, _ = canon(os.path.basename(f)[:-6]); g = re.search(r"Generation:.*?([0-9.]+) tokens-per-sec", open(f).read())
    if g: rows.setdefault(nm, {})['tgm'] = round(float(g.group(1)))
def cell(v): return "—" if v is None else (f"{v:.1f}" if isinstance(v,float) else str(v))
ranked = sorted(META, key=lambda k: -(rows.get(k,{}).get('hg') or rows.get(k,{}).get('hm') or -1))
medal = {0:"🥇",1:"🥈",2:"🥉"}
lines = ["| Rank | Model | Vendor / gen | Params | quant · size (lcpp) | HE+ (llama.cpp) | HE+ (MLX) | gen t/s (lcpp) | gen t/s (MLX) | empty (lcpp) | empty (MLX) |",
         "|---|---|---|---|---|---|---|---|---|---|---|"]
rk = 0
for k in ranked:
    r = rows.get(k, {}); has = r.get('hg') is not None or r.get('hm') is not None
    badge = medal.get(rk, str(rk+1)) if has else "—"
    if has: rk += 1
    v, p = META[k]
    mark = " ⁺" if k in REASONING else ""
    lines.append(f"| {badge} | {k}{mark} | {v} | {p} | {cell(r.get('qz'))} | {cell(r.get('hg'))} | {cell(r.get('hm'))} | {cell(r.get('tgg'))} | {cell(r.get('tgm'))} | {cell(r.get('eg'))} | {cell(r.get('em'))} |")
TABLE = "\n".join(lines)
FOOTNOTE = (
 "**⁺ = reasoning model — its score is a FLOOR, not a measurement.**\n\n"
 "These models emit a `<think>` block before answering. llama.cpp with `--jinja` splits that "
 "into `reasoning_content`, so a model that does not finish thinking within the token cap "
 "returns **empty `content`** — and EvalPlus scores an empty response identically to a wrong "
 "answer. Confirmed directly against a live server:\n\n"
 "```\nHumanEval/10 -> finish_reason=length, content=0 chars, "
 "reasoning_content=14451 chars, completion_tokens=4096\n```\n\n"
 "The model wrote ~14,500 characters of reasoning and never emitted one character of answer. "
 "This is **not** quantisation damage: it reproduces on a vanilla Q5_K_XL build on different "
 "hardware. Read the `empty` columns as the size of this effect — Qwen3.8-27B lost **29 of 164** "
 "tasks (17.7%) to it, capping its achievable score at 82.3% before any code was judged.\n\n"
 "The cap was already raised once (768 -> 4096) after it scored Qwen3.5-9B a false 42.7. "
 "4096 is still not enough for the newest reasoning models. See "
 "[#7](https://github.com/CryptoJones/MacminiM2Pro_ModelShowdown/issues/7)."
)
done = sum(1 for k in META if rows.get(k,{}).get('hg') is not None)
status = ("✅ **GGUF PASS COMPLETE.** MLX results remain unmeasured for models marked `—`."
          if done == len(META)
          else f"⚠️ **IN PROGRESS** — {done}/{len(META)} models have llama.cpp quality; MLX pass fills the rest.")
readme = open(os.path.join(HERE,"README.md")).read()
# replace everything from the "## Results" header up to (not including) "## Reading"
readme = re.sub(r"## Results.*?(?=## Reading)",
                f"## Results — HumanEval+ pass@1 (quality) + generation t/s\n\n{status} `—` = not measured.\n\n{TABLE}\n\n{FOOTNOTE}\n\n",
                readme, flags=re.DOTALL)
open(os.path.join(HERE,"README.md"),"w").write(readme)
print("README updated;", done, "models with quality")
