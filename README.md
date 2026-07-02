<p align="center"><em>Proudly Made in Nebraska. Go Big Red! 🌽 <a href="https://xkcd.com/2347/">https://xkcd.com/2347/</a></em></p>

# MacminiM2Pro_ModelShowdown

Local coding-LLM showdown on a **Mac mini (Apple M2 Pro, 16 GB unified memory)** — every number measured first-hand on this machine, not copied from leaderboards.

**Two questions:**
1. Which open-weight coding model is best for software engineering that fits **comfortably (≤ ~10 GB peak)** on 16 GB?
2. Which local runtime hosts it best — **`llama.cpp` (Metal, GGUF)** vs **`MLX` (4-bit)**?

**How:** quality = **EvalPlus HumanEval+** (164 problems, executed, greedy, pass@1); speed = `llama-bench` (llama.cpp) / `mlx_lm` (MLX); 4-bit across the board. See [METHODOLOGY.md](METHODOLOGY.md).

> ⚠️ **STATUS: run in progress.** The GGUF pass is filling in; the MLX pass runs after it. `—` = not yet measured. This README is updated as cells complete (auto-committed by the completion watcher).

## Results — HumanEval+ pass@1 (quality) + generation t/s

✅ **COMPLETE.** `—` = not measured.

| Rank | Model | Vendor / gen | Params | HE+ (llama.cpp) | HE+ (MLX) | gen t/s (lcpp) | gen t/s (MLX) |
|---|---|---|---|---|---|---|---|
| 🥇 | Qwen3.5-9B | Alibaba 2026 (reasoning/MTP) | 9B | 90.2 | 70.7 | 25 | 37 |
| 🥈 | ornith-9B | DeepReinforce 2026 (Qwen3.5-based) | 9B | 88.4 | 84.8 | 25 | 37 |
| 🥉 | Qwen2.5-Coder-14B | Alibaba 2024 (dedicated coder) | 14B | 87.2 | — | 17 | 22 |
| 4 | gpt-oss-20b | OpenAI | 20B (MoE) | 87.2 | — | 52 | — |
| 5 | Qwen2.5-Coder-7B | Alibaba 2024 (dedicated coder) | 7B | 84.1 | 83.5 | 34 | 43 |
| 6 | NVIDIA-Nemotron-9B | NVIDIA 2026 (reasoning) | 9B | 82.3 | — | 17 | — |
| 7 | Phi-4 | Microsoft | 14B | 82.3 | — | 17 | — |
| 8 | Gemma-4-12B-Coder | community finetune of Gemma-4-12B (fable5/composer2.5) | 12B | 82.3 | — | 20 | — |
| 9 | DeepSeek-V2-Lite | DeepSeek 2024 (MoE, 2.4B active) | 16B | 76.8 | — | 69 | 87 |
| 10 | Gemma-4-12B | Google 2026 | 12B | 68.3 | — | 18 | — |
| 11 | IBM-Granite-8B | IBM / Red Hat | 8B | 65.2 | 62.8 | 30 | 37 |
| 12 | CodeGemma-7B | Google 2024 | 7B | 50.0 | — | 29 | 30 |

## Reading so far
- **Quality leader: Qwen3.5-9B (90.2 % HE+)** — a newest-gen *reasoning* 9B beating the dedicated Qwen2.5-Coder-14B at 2/3 the size. ornith-9B (also Qwen3.5-based) is right behind at 88.4 %.
- **Speed leader: DeepSeek-V2-Lite MoE** — ~69/87 t/s, 3–4× the dense models (only ~2.4B params active), but lower quality (76.8 %).
- **Runtime pattern (so far):** MLX wins generation throughput on every model measured; llama.cpp wins prefill.
- **Gotcha worth noting:** reasoning models were initially scored falsely low (Qwen3.5-9B showed 42.7 %) because EvalPlus's default 768-token cap truncated their `<think>` before the code. Raising it to 4096 fixed it — see METHODOLOGY.

Final model + runtime verdict lands here once the full 11 × 2 matrix is complete.
