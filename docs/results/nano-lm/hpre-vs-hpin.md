# H-PRE smoke — prefetch H2D under PIN vs H-PIN

Same top-k soft cache, STAG curriculum, and pinned tensors; H-PRE overlaps H2D+expand of step i+1 with compute of step i. Not H-ASYNC (cache build overlap). Kill if |Δlp| > ε or no ms/step win.
Recipe: `seq_lo=6`, `n_stages=4`, `steps=30`, `top_k=64`, mode `PIN + 1-deep H2D prefetch stream (cache already built)`.

| family | mean teacher_lp | Δ lp | mean ms/step | Δ ms/step | mean train_wall_s | n |
|--------|-----------------|------|--------------|-----------|------------------|---|
| H-PIN | -16.6988 | — | 6.8 | — | 0.20 | 3 |
| H-PRE | -16.6988 | +0.0000 | 6.1 | -0.7 | 0.18 | 3 |

**Decision: PROMOTE (prefetch H2D under PIN)**

Tip H-PIN / H-TOP util unchanged unless PROMOTE. Train I/O deepen.

Commands: `npm run nano:pre` → `npm run nano:pre:report`.
