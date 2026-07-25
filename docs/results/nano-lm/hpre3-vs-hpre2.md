# H-PRE3 smoke — 3-deep prefetch under PRE2 vs H-PRE2

Same ADAMF I/O stack; only prefetch_depth differs (3 vs 2). Kill if |Δlp| > ε or no ms/step win.
Recipe: `seq_lo=6`, `n_stages=4`, `steps=30`, `top_k=64`, mode `ADAMF I/O + prefetch_depth=3 vs depth=2`.

| family | mean teacher_lp | Δ lp | mean ms/step | Δ ms/step | mean train_wall_s | n |
|--------|-----------------|------|--------------|-----------|------------------|---|
| H-PRE2 | -16.6988 | — | 6.6 | — | 0.20 | 3 |
| H-PRE3 | -16.6988 | +0.0000 | 6.0 | -0.7 | 0.18 | 3 |

**Decision: PROMOTE (3-deep prefetch under PRE2)**

Tip H-PRE2 util unchanged unless PROMOTE. Train I/O deepen.

Commands: `npm run nano:pre3` → `npm run nano:pre3:report`.
