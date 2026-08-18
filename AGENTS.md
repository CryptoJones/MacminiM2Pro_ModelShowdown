# AGENTS.md — rules for anyone (human or agent) running this benchmark

Read this before touching the matrix. Every rule here exists because breaking it already cost
real time.

---

## 1. ALWAYS archive a run into the repo. Never leave results in scratch.

`~/showdown-scratch` **gets wiped**. Raw generations survived for only 2 of 15 models, which
made most of the matrix permanently un-auditable and forced a whole investigation
([#7](https://github.com/CryptoJones/MacminiM2Pro_ModelShowdown/issues/7)).

`run_quality.sh` and `run_mlx.sh` now call `harness/archive_run.sh` automatically. If you run
EvalPlus **by hand**, archive it yourself:

```sh
harness/archive_run.sh <label> <lcpp|mlx> <evalplus-root> [model-path] [server-cmd]
```

That writes, all inside the repo:

| Path | Contents |
|---|---|
| `results/raw/<id>/` | the generations — `*.raw.jsonl` (pre-sanitisation), the sanitised `.jsonl`, and `*_eval_results.json` |
| `results/runs/<id>.json` | provenance — server command, harness commit, model path + size + **sha256**, host, macOS version, CPU idle %, task/empty counts |
| `results/<id>.empties` | empty-completion count, consumed by `update_readme.py` |

**Keep `*.raw.jsonl`.** The sanitised file cannot tell "the server returned nothing" from "the
model wrote something unusable". Only the raw file can.

## 2. An EMPTY response is not a wrong answer.

The harness scores both as a failed task, so a flaky server silently costs a model points. The
matrix therefore carries **`empty (lcpp)`** and **`empty (MLX)`** columns. Always report them
next to a score.

Measured, both runtimes affected, no clean pattern:

| Model | empty (llama.cpp) | empty (MLX) |
|---|---|---|
| Qwythos-9B-v2 | 8 / 164 | **26 / 164** |
| Ternary-Bonsai-27B | **33 / 164** | 0 / 164 |

Qwythos is worse on MLX; Ternary is worse on llama.cpp. **Do not assume one runtime is the
flaky one** — an earlier analysis claimed exactly that and was wrong, because a glob matched
the llama.cpp directory twice (the MLX ternary run lives under `mlx_runs/eval/`, not `eval/`).
**Resolve run directories by explicit path, never by wildcard.**

## 3. The 4096-token cap applies to BOTH runtimes. Do not "fix" it again.

It lives in `evalplus/provider/base.py` (`max_new_tokens: int = 4096`) and is passed via
`provider/openai.py`. Both llama.cpp and MLX inherit it. This was investigated and **ruled out**
as a cause of low MLX scores — surviving MLX generations show zero unclosed `<think>` blocks and
a *longer* median than llama.cpp's.

Reasoning models still need it: with EvalPlus's stock 768 cap, Qwen3.5-9B scored a false 42.7.

## 4. Speed numbers require a verifiably quiet box.

**Check actual CPU idle before timing anything** — target ~88%+:

```sh
top -l 2 -n 0 | grep "^CPU usage"
```

Spotlight/Time Machine/photoanalysis are the documented offenders, but on 2026-08-18 the real
culprit was the **Buzz agent fleet** — six `buzz-dev-mcp` processes at 60-84% CPU holding the
box at 51% idle. Killing them is not enough; ten `com.cryptojones.buzz*` launchd agents have
KeepAlive and respawn instantly. Use `launchctl bootout gui/501/<label>`, and **restore them
afterwards**.

Quality (pass@1) is *not* load-sensitive — only speed is. A contended box makes a quality run
slower, not wrong.

## 5. Withdraw, don't delete.

A result that cannot be trusted is renamed `results/<id>.evalplus.withdrawn` (so the matrix
shows `—`) and the reason is recorded in `METHODOLOGY.md`. Never `rm` a measurement.

## 6. Repo conventions

- **Public repo → feature branch + PR.** Never commit straight to `main`.
- Every PR body ends with: `Proudly Made in Nebraska. Go Big Red! 🌽 https://xkcd.com/2347/`
- `BACKLOG.md` mirrors the GitHub Issues tab; adding to one means adding to the other.
- One model at a time on a 16 GB box: pull from telesto → test → delete. Transfer XOR compute.

## 7. Reading llama.cpp's model line

`llama-bench` prints the **architecture**, not the model name. Qwen3.8-27B displays as
`qwen35 27B` because it uses the `qwen35` architecture — the same string Qwen3.5-9B shows.
Tell them apart by parameter count (27.32 B vs 9.20 B). Unsloth dynamic quants also report a
nominal `file_type`: `Qwen3.8-27B-UD-IQ2_M` prints as "Q4_K - Small" but is ~2.8 bits/weight.

---

*Proudly Made in Nebraska. Go Big Red! 🌽 <https://xkcd.com/2347/>*
