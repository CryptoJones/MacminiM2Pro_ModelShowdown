# BACKLOG — MacminiM2_Model_Results

Mirror of the GitHub Issues tab. Every item ↔ a GitHub issue (linked once the repo is pushed).

## In progress
- [ ] Complete GGUF (llama.cpp) HumanEval+ pass for all 11 models
- [ ] Complete MLX HumanEval+ pass for all 11 models (full 11 x 2 matrix)
- [ ] llama-bench + mlx speed/fit for all 11 on both runtimes
- [ ] Qwen3.8-27B `UD-IQ2_M` (llama.cpp): HumanEval+ pass — **reasoning model, needs the 4096-token cap**
- [x] Qwen3.8-27B `UD-IQ2_M` (llama.cpp): llama-bench pp512/tg128 under quiet conditions — pp512 74.14, tg128 7.79 (2026-08-18, box at 95% idle)
- [ ] Retry on empty completions before recording a failure ([#7](https://github.com/CryptoJones/MacminiM2Pro_ModelShowdown/issues/7))
- [ ] Capture `mlx_lm.server` stderr — `*.mlxserver.log` files are 0 bytes ([#7](https://github.com/CryptoJones/MacminiM2Pro_ModelShowdown/issues/7))
- [x] Archive every run into the repo (`results/raw/` + `results/runs/` provenance) — `harness/archive_run.sh`, wired into both harnesses
- [x] Publish per-cell empty-response counts in the matrix (`empty (lcpp)` / `empty (MLX)`)
- [ ] Final verdict: best coding model (quality within ≤10 GB) + best runtime (MLX vs llama.cpp)

## Done
- [x] Build llama.cpp locally (commit 57e8718fd, Metal) and verify
- [x] Author EvalPlus + homegrown executable harness; fix macOS `setrlimit` incompatibility
- [x] Qwen2.5-Coder-14B GGUF: HE 90.9 / HE+ 87.2
- [x] Qwen2.5-Coder-7B GGUF: HE 87.8 / HE+ 84.1
- [x] Pre-stage GGUF + MLX of all models on telesto; pull-over-LAN-between-tests pipeline

## Candidate models (11)
Qwen2.5-Coder-14B, Qwen2.5-Coder-7B, Qwen3.5-9B, DeepSeek-Coder-V2-Lite-16B, ornith-9B,
NVIDIA-Nemotron-Nano-9B-v2, IBM Granite-3.3-8B, Microsoft Phi-4, Gemma-4-12B, CodeGemma-7B, gpt-oss-20b.

*Proudly Made in Nebraska. Go Big Red! 🌽 <https://xkcd.com/2347/>*
