# H-PIN smoke — pinned + non_blocking H2D vs H-TOP

Same top-k soft cache and STAG curriculum; only H2D path differs.
Kill if quality < TOP−ε or no train ms/step win.
Recipe: `seq_lo=6`, `n_stages=4`, `steps=30`, `top_k=64`, mode `pin_memory + non_blocking H2D`.

| family | mean teacher_lp | Δ lp | mean ms/step | Δ ms/step | mean train_wall_s | n |
|--------|-----------------|------|--------------|-----------|------------------|---|
| H-TOP | -16.6988 | — | 7.1 | — | 0.21 | 3 |
| H-PIN | -16.6988 | +0.0000 | 5.9 | -1.2 | 0.18 | 3 |

**Decision: PROMOTE (pinned H2D vs TOP)**

Tip H-TOP util unchanged unless PROMOTE. Train I/O systems deepen.

Commands: `npm run nano:pin` → `npm run nano:pin:report`.
