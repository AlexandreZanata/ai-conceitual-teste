# Nano-LM lab comparison vs base model

**Run:** `npm run nano:lab` → `results/nano-lm/lab-gpu-lab/runs.jsonl`  
**Frozen weights:** [`roneneldan/TinyStories-1M`](https://huggingface.co/roneneldan/TinyStories-1M) (Eldan & Li, [arXiv:2305.07759](https://arxiv.org/abs/2305.07759))  
**Base decode (paper-style):** **AR** = temperature 0.8 + top-p 0.9, one sample (`K=1`)  
**Hypotheses:** **BoN** (best-of-32) and **Lookahead MAE** (`K=48`, `B=4`, `H=8`) on the **same** weights/prompts/seeds

> Metric: length-normalized **self** mean log-prob (higher / less negative = better under the frozen model).  
> Not GPT-4 teacher grades from the TinyStories paper.

## Head-to-head (n=4: prompts p01–p02 × seeds 0–1)

| Method | Role | mean_logprob | Δ vs AR | win vs AR | wall_ms | token_evals | cost vs AR |
|--------|------|--------------|---------|-----------|---------|-------------|------------|
| **AR** | **Base model decode** | **−1.062** | 0 | — | **280** | **64** | 1× |
| **BoN** | Hypothesis (pick best of N) | **−0.679** | **+0.383** | **4/4 (100%)** | 406 | 2048 | ~1.5× time, 32× evals |
| **MAE** | Hypothesis (lookahead commit) | **−0.878** | **+0.184** | **3/4 (75%)** | 1550 | 9216 | ~5.5× time, 144× evals |

## Verdict

1. **Base (AR)** is cheapest and weakest on self log-prob in this smoke slice.
2. **BoN clearly beats the base** on every (prompt, seed): +0.38 mean log-prob, only ~1.5× wall time thanks to batched GPU sampling.
3. **MAE also beats the base on average** (+0.18, 75% win-rate) but **loses to BoN** on quality and is much more expensive (and triggered CUDA OOM warnings at `mae_k=48` on an 8 GiB laptop GPU).

So relative to the TinyStories-1M **base decode**, multi-attempt search helps; on this run **Best-of-N is the better quality/cost tradeoff** than Lookahead MAE.

## Caveats

- Smoke prompts only (2); formal set is 8 prompts in `eval_prompts.yaml`.
- OOM warnings during BoN/MAE — allocator recovered, but configs should stay within VRAM.
- End-of-run SM util 0% is idle snapshot after decode finished (hist sparklines show real load).
- Paper’s GPT-4 grammar/creativity/consistency scores are **not** measured here.

## Raw paths

- JSONL: `results/nano-lm/lab-gpu-lab/runs.jsonl`
- Aggregate: `results/nano-lm/lab-gpu-lab/lab-summary.md`
- Config: `nano_lm/configs/lab_gpu.json`
