# Nano-LM Track — Research Protocol

> **Active lab.** Caps: ≤80 / ≤200 / cyclo ≤10.  
> EvoGen C++ Domain is frozen (`docs/archive/evogen/`).

## Hypothesis

Multi-attempt evaluate (many candidate futures scored, one committed) can match or beat sequential autoregressive (AR) quality on a tiny specialized LM, under comparable or better wall-clock / token-eval tradeoffs — without relying only on long purely sequential next-token chains.

Wave W **COMPLETE** — curated public programming + frontier corpora and PACK efficiency on those domains ([wave-w-summary.md](results/nano-lm/wave-w-summary.md)). Wave X **PARKED**. Lab: `.local/pesquisa.md`.

## Academic baseline

| Item | Value |
|------|-------|
| Challenge | TinyStories story continuation |
| Paper | Eldan & Li, [arXiv:2305.07759](https://arxiv.org/abs/2305.07759) |
| Frozen model | [`roneneldan/TinyStories-1M`](https://huggingface.co/roneneldan/TinyStories-1M) |
| Tokenizer | `EleutherAI/gpt-neo-125M` |
| Weights | Frozen (no retraining in v1) |

## Methods (same weights, same prompts)

1. **AR** — temperature 0.8, top-p 0.9, single sample.
2. **Best-of-N (BoN)** — N independent AR completions; commit argmax of length-normalized mean log-prob.
3. **Lookahead MAE** — every block of B tokens: sample K candidate blocks; score each by mean log-prob of an extra H sampled tokens (look-ahead fitness); commit the winning block via argmax. Fitness is **not** the immediate block log-prob (avoids collapsing to greedy).

Smoke: `N=8`, `K=16`, `B=4`, `H=8`, `max_new_tokens=64`.  
Formal: `N=32`, `K=32`, `B=4`, `H=16`, `max_new_tokens=128`.

## Metrics (automated; no GPT-4 teacher)

- Length-normalized mean log-prob of completion (self-model)
- Distinct-1 / Distinct-2
- Wall-ms and token-evals (compute proxy)
- Win-rate vs AR on mean log-prob
- Optional: teacher NLL under TinyStories-33M (formal config only; skip if unavailable)

**Gap vs paper:** GPT-4 “teacher” grading is out of v1.

## Layout

Code and configs live under `nano_lm/`. Run outputs under `results/nano-lm/` (gitignored). Summaries under `docs/results/nano-lm/`.

**Terminal lab:** `npm run nano:lab` (GPU-heavy batched fp16) — live SM/VRAM/power bars, util sparklines, per-CPU-core busy %, AR vs BoN vs MAE table. Requires CUDA.

## Non-goals (v1)

- Retraining TinyStories from scratch
- GPT-4 automatic grading
- Merging PyTorch into the C++ evolutionary loop
- Primary baseline ≥50M parameters
