# H-TOPK smoke — top-k sweep vs tip k=64

Equal STAG steps; offline cache sliced from max-k=128 (sorted top-k).
Kill if best k ≤ tip k=64 on (teacher_lp, ms/step).
Recipe: `seq_lo=6`, `n_stages=4`, `steps=30`, sweep=`[16, 32, 64, 128]`.

| top_k | mean teacher_lp | Δ lp vs tip | mean ms/step | Δ ms/step | mean train_wall_s | n |
|-------|-----------------|-------------|--------------|-----------|------------------|---|
| 16 | -16.9578 | -0.2591 | 7.1 | +1.4 | 0.21 | 3 |
| 32 | -16.7268 | -0.0280 | 5.6 | -0.1 | 0.17 | 3 |
| 64 **(tip)** | -16.6988 | — | 5.7 | — | 0.17 | 3 |
| 128 | -16.8316 | -0.1328 | 5.7 | -0.0 | 0.17 | 3 |

**Decision: PROMOTE (best k=32 beats tip k=64)**

Commands: `npm run nano:topk` → `npm run nano:topk:report`.
