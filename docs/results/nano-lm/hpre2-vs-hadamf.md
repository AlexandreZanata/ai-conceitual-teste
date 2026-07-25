# H-PRE2 smoke — 2-deep prefetch under ADAMF vs H-ADAMF

Same top-k soft cache, STAG curriculum, HALF wire, and fused AdamW; only prefetch_depth differs (2 vs 1). Kill if |Δlp| > ε or no ms/step win.
Recipe: `seq_lo=6`, `n_stages=4`, `steps=30`, `top_k=64`, mode `ADAMF I/O + prefetch_depth=2 vs depth=1`.

| family | mean teacher_lp | Δ lp | mean ms/step | Δ ms/step | mean train_wall_s | n |
|--------|-----------------|------|--------------|-----------|------------------|---|
| H-ADAMF | -16.6988 | — | 6.3 | — | 0.19 | 3 |
| H-PRE2 | -16.6988 | +0.0000 | 5.5 | -0.8 | 0.17 | 3 |

**Decision: PROMOTE (2-deep prefetch under ADAMF)**

Tip H-ADAMF / H-PRE util unchanged unless PROMOTE. Train I/O deepen.

Commands: `npm run nano:pre2` → `npm run nano:pre2:report`.
