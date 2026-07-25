# Formal H-PRE vs H-PIN (prefetch H2D under PIN)

Source: `results/nano-lm/formal-hpre/formal.json`
Wall clock: 140.0s

Same top-k soft cache and STAG curriculum; only H2D scheduling differs.
Fit≠eval. Gate: |Δlp| ≤ ε **and** train ms/step < PIN.
Recipe: `seq_lo=6`, `n_stages=4`, `steps=120`, `top_k=64`, mode `PIN + 1-deep H2D prefetch stream (cache already built)`.

| family | mean teacher_lp | Δ lp | mean ms/step | Δ ms/step | mean train_wall_s | n |
|--------|-----------------|------|--------------|-----------|------------------|---|
| H-PIN | -12.4946 | — | 14.6 | — | 1.75 | 3 |
| H-PRE | -12.4946 | +0.0000 | 14.5 | -0.1 | 1.74 | 3 |

**Decision:** PROMOTE (prefetch H2D under PIN)

Tip H-PIN / H-TOP util unchanged. Train I/O deepen.

Commands: `npm run nano:formal:hpre` → `npm run nano:formal:hpre:report`.
