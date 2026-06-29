#!/usr/bin/env python3
"""Regenerate README.md results table from results/*.evalplus / *.bench / *.speed."""
import os, glob, re, sys
HERE = os.path.dirname(os.path.abspath(__file__))
R = os.path.join(HERE, "results")
META = {  # canonical -> (vendor/gen, params)
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
}
NAME = {'q14b':'Qwen2.5-Coder-14B','qwen25c-14b':'Qwen2.5-Coder-14B','q7b':'Qwen2.5-Coder-7B','qwen25c-7b':'Qwen2.5-Coder-7B',
 'q35-9b':'Qwen3.5-9B','dsc':'DeepSeek-V2-Lite','dsc-lite':'DeepSeek-V2-Lite','ornith-9b':'ornith-9B',
 'nemotron-9b':'NVIDIA-Nemotron-9B','granite-8b':'IBM-Granite-8B','codegemma-7b':'CodeGemma-7B',
 'gemma4-12b':'Gemma-4-12B','phi4':'Phi-4','gptoss-20b':'gpt-oss-20b','gemmacoder':'Gemma-4-12B-Coder'}
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
for f in glob.glob(R+"/*.speed"):
    nm, _ = canon(os.path.basename(f)[:-6]); g = re.search(r"Generation:.*?([0-9.]+) tokens-per-sec", open(f).read())
    if g: rows.setdefault(nm, {})['tgm'] = round(float(g.group(1)))
def cell(v): return "—" if v is None else (f"{v:.1f}" if isinstance(v,float) else str(v))
ranked = sorted(META, key=lambda k: -(rows.get(k,{}).get('hg') or rows.get(k,{}).get('hm') or -1))
medal = {0:"🥇",1:"🥈",2:"🥉"}
lines = ["| Rank | Model | Vendor / gen | Params | HE+ (llama.cpp) | HE+ (MLX) | gen t/s (lcpp) | gen t/s (MLX) |",
         "|---|---|---|---|---|---|---|---|"]
rk = 0
for k in ranked:
    r = rows.get(k, {}); has = r.get('hg') is not None or r.get('hm') is not None
    badge = medal.get(rk, str(rk+1)) if has else "—"
    if has: rk += 1
    v, p = META[k]
    lines.append(f"| {badge} | {k} | {v} | {p} | {cell(r.get('hg'))} | {cell(r.get('hm'))} | {cell(r.get('tgg'))} | {cell(r.get('tgm'))} |")
TABLE = "\n".join(lines)
done = sum(1 for k in META if rows.get(k,{}).get('hg') is not None)
status = ("✅ **COMPLETE.**" if done == len(META) else f"⚠️ **IN PROGRESS** — {done}/{len(META)} models have llama.cpp quality; MLX pass fills the rest.")
readme = open(os.path.join(HERE,"README.md")).read()
# replace everything from the "## Results" header up to (not including) "## Reading"
readme = re.sub(r"## Results.*?(?=## Reading)",
                f"## Results — HumanEval+ pass@1 (quality) + generation t/s\n\n{status} `—` = not measured.\n\n{TABLE}\n\n",
                readme, flags=re.DOTALL)
open(os.path.join(HERE,"README.md"),"w").write(readme)
print("README updated;", done, "models with quality")
