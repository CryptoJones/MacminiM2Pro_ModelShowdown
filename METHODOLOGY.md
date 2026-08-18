# Methodology

## Hardware
Mac mini, Apple **M2 Pro, 16 GB** unified memory, macOS. Homelab archive/stage node **telesto** (Ubuntu, 390 GB free) on the LAN.

## Budget
"Fits comfortably, not tight" = **≤ ~10 GB peak** at 4-bit (leaves ~6 GB for the OS + apps). gpt-oss-20b (~13 GB) is included as an explicit budget-edge data point.

## Quality — EvalPlus HumanEval+
- `evalplus==0.3.1`, dataset `humaneval`, **greedy** decode, executed **pass@1** (base HumanEval + augmented `+` tests).
- Reasoning models receive a **4096-token generation cap**; EvalPlus's 768-token default can truncate reasoning before the final code.
- Generation hits each model's OpenAI-compatible server (`llama-server --jinja` for GGUF; `mlx_lm.server` for MLX); EvalPlus sanitizes + executes.
- **macOS fix:** EvalPlus's `reliability_guard` calls `setrlimit` with values macOS rejects (`ValueError: current limit exceeds maximum limit`), making every task falsely "timeout" → pass@1 = 0. Patched the venv's `evalplus/eval/utils.py` to tolerate the `setrlimit` failure. Validated (Qwen2.5-Coder-7B → 84.1 % HE+, a sane number).

## Speed / fit
- **llama.cpp:** `llama-bench -p 512 -n 128 -r 3` → pp512 (prefill t/s), tg128 (gen t/s). Binary built locally @ `57e8718fd` (Metal).
  - Ternary-Bonsai-27B requires Prism ML's llama.cpp fork; its Q2_0 run used build `9fcaed763` (`9596`) with the same benchmark arguments.
  - Caveat: llama.cpp **mmaps** GGUF weights, so process RSS understates memory (esp. MoE). Fit is reported as model-on-Metal size + KV.
- **MLX:** `mlx_lm.generate --verbose` → prompt/gen t/s + reported **peak memory** (the honest MLX footprint).

## Measurement discipline
- The Mac is **either transferring or evaluating, never both** (concurrent I/O skews t/s). A single serial driver enforces this; transfers happen only with no server running.
- Models are downloaded **once on telesto** (sequentially, to avoid HF throttling), then **pulled over LAN** to the Mac between tests. telesto is the archive; the Mac copy is transient and deleted after each model.

## Quant parity
4-bit across runtimes (GGUF `Q4_K_M` ≈ MLX 4-bit; gpt-oss uses native MXFP4), except two deliberate sub-4-bit entries: Ternary-Bonsai-27B's native ternary Q2_0 GGUF, and Qwen3.8-27B at Unsloth Dynamic `UD-IQ2_M` (10.3 GB) — a 27B dense model has no 4-bit quant that fits 16 GB (`Q4_K_M` is 17.1 GB), so 2-bit is the only way it runs here at all. Read that row as *"can a heavily-quantised 27B beat a comfortable 9B?"*, not as a like-for-like quality comparison. Quant schemes differ slightly between runtimes, which is *why* both are measured — quality is not assumed to transfer.

*Proudly Made in Nebraska. Go Big Red! 🌽 <https://xkcd.com/2347/>*

## Withdrawn MLX quality cells (2026-08-18)

Two MLX HumanEval+ cells were withdrawn from the matrix and now show `—`. The numbers are
not deleted — the result files are kept in `results/` renamed to `*.evalplus.withdrawn`, so
the decision stays auditable.

| Cell | Withdrawn value | Reason |
|---|---|---|
| Qwen3.5-9B, HE+ (MLX) | 70.7 | 19.5 points below its llama.cpp score (90.2) — nearly 3× the next-largest runtime gap in the matrix, and its raw generations were cleaned from scratch so the result cannot be audited. |
| Qwythos-9B-v2, HE+ (MLX) | 75.0 | 21 of its 164 MLX requests returned an **empty** completion where llama.cpp answered the same task normally (~12.8 points of spurious failure). |

### The underlying defect: empty responses scored as wrong answers

The harness does not distinguish "the model answered incorrectly" from "the server returned
nothing." Both count as a failed task, so a flaky server silently costs a model points. The
matrix therefore carries `empty (lcpp)` and `empty (MLX)` columns.

Measured on the runs whose raw generations survive:

| Model | empty (llama.cpp) | empty (MLX) |
|---|---|---|
| Qwythos-9B-v2 | 8 / 164 (4.9%) | **26 / 164 (15.9%)** |
| Ternary-Bonsai-27B | **33 / 164 (20.1%)** | 0 / 164 (0%) |

These are **raw**, pre-sanitisation, zero-length responses, not extraction failures.

**Neither runtime is systematically at fault.** Qwythos is far worse on MLX (21 of its 26
empties are tasks llama.cpp answered fine); Ternary-Bonsai-27B is the reverse, with 33 empties
on llama.cpp and *none* on MLX. No task came back empty across all four runs. The effect is
per-model and hits both runtimes, so empty counts must be published per cell rather than
attributed to a runtime.

> **Correction (2026-08-18).** An earlier revision of this section claimed Ternary-Bonsai-27B
> produced "the identical set of 33 empties on both runtimes," and concluded those were
> model-deterministic and fairly scored. That was wrong. The glob used to locate the runs
> matched the llama.cpp directory twice — the MLX ternary run lives under
> `~/showdown-scratch/mlx_runs/eval/`, not `~/showdown-scratch/eval/` — so the llama.cpp file
> was compared against itself. Resolve run directories by explicit path, never by wildcard.

**Not the 4096-token cap.** That was checked and ruled out. The cap lives in
`evalplus/provider/base.py` (`max_new_tokens: int = 4096`) and is passed through
`provider/openai.py`, so both runtimes inherit it; it predates these runs. The surviving MLX
generations show zero unclosed `<think>` blocks, no pile-up at any ceiling, and a *longer*
median than llama.cpp's (617 vs 570 chars). Nothing was truncated.

### Ternary-Bonsai-27B's llama.cpp score carries 33 empties

Its 72.0 is depressed by ~20 points of non-responses, while its MLX 65.9 has none. The cell is
**retained rather than withdrawn** — now that the empty counts are published, a reader can see
and discount it. Withdrawing it would hide a measurement that is merely qualified, not wrong.

### Known gaps

Raw generations survive for only 2 of the 15 models; scratch cleanup removed the rest, so
their empty counts show `—` and cannot be recovered. Going forward every run is archived into
`results/raw/` with a provenance manifest in `results/runs/` — see `AGENTS.md`.
