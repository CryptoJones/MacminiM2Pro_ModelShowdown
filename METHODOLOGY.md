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
4-bit across runtimes (GGUF `Q4_K_M` ≈ MLX 4-bit; gpt-oss uses native MXFP4), except Ternary-Bonsai-27B's native ternary Q2_0 GGUF. Quant schemes differ slightly between runtimes, which is *why* both are measured — quality is not assumed to transfer.

*Proudly Made in Nebraska. Go Big Red! 🌽 <https://xkcd.com/2347/>*
