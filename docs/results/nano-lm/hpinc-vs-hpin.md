# H-PINC smoke — torch.compile under PIN train vs H-PIN

Same top-k soft cache, STAG curriculum, and pinned H2D; only compile differs.
Compile warmup is untimed. Kill if |Δlp| > ε vs H-PIN or no ms/step win.
Recipe: `seq_lo=6`, `n_stages=4`, `steps=30`, `top_k=64`, mode `PIN train + torch.compile(default); warmup untimed`.

| family | mean teacher_lp | Δ lp | mean ms/step | Δ ms/step | mean train_wall_s | n |
|--------|-----------------|------|--------------|-----------|------------------|---|
| H-PIN | -16.6988 | — | 7.0 | — | 0.21 | 3 |
| H-PINC | -16.6988 | +0.0000 | 970.6 | +963.6 | 29.12 | 3 |

**Decision: KILL (no train step-time win vs H-PIN)**

Tip H-PIN / H-TOP util unchanged unless PROMOTE. Train I/O deepen.

Commands: `npm run nano:pinc` → `npm run nano:pinc:report`.
