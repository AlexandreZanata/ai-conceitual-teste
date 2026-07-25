# Formal H-PRE3 vs H-PRE2 (3-deep prefetch under PRE2)

Source: `results/nano-lm/formal-hpre3/formal.json`
Wall clock: 151.7s

Same ADAMF I/O path; only prefetch_depth differs (3 vs 2).
Fit≠eval. Gate: |Δlp| ≤ ε **and** train ms/step < PRE2.
Recipe: `seq_lo=6`, `n_stages=4`, `steps=120`, `top_k=64`, mode `ADAMF I/O + prefetch_depth=3 vs depth=2`.

| family | mean teacher_lp | Δ lp | mean ms/step | Δ ms/step | mean train_wall_s | n |
|--------|-----------------|------|--------------|-----------|------------------|---|
| H-PRE2 | -12.4946 | — | 14.4 | — | 1.73 | 3 |
| H-PRE3 | -12.4946 | +0.0000 | 14.1 | -0.3 | 1.70 | 3 |

**Decision:** PROMOTE (3-deep prefetch under PRE2)

Tip H-PRE2 util unchanged. Train I/O deepen.

Commands: `npm run nano:formal:hpre3` → `npm run nano:formal:hpre3:report`.
