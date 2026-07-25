# H-HALF smoke — fp16-wire H2D under PRE vs H-PRE

Same top-k soft cache, STAG curriculum, and PRE prefetch; H-HALF keeps topk_val fp16 across H2D then casts on GPU before expand. Kill if |Δlp| > ε vs H-PRE or no ms/step win.
Recipe: `seq_lo=6`, `n_stages=4`, `steps=30`, `top_k=64`, mode `PRE prefetch; HALF keeps topk_val fp16 on H2D then GPU cast`.

| family | mean teacher_lp | Δ lp | mean ms/step | Δ ms/step | mean train_wall_s | n |
|--------|-----------------|------|--------------|-----------|------------------|---|
| H-PRE | -16.6988 | — | 7.1 | — | 0.21 | 3 |
| H-HALF | -16.6988 | +0.0000 | 6.2 | -1.0 | 0.18 | 3 |

**Decision: PROMOTE (fp16-wire H2D under PRE)**

Tip H-PRE / H-PIN util unchanged unless PROMOTE. Train I/O deepen.

Commands: `npm run nano:half` → `npm run nano:half:report`.
