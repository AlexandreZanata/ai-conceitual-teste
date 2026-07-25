# Formal H-TPACK — PRE3 ms/step pack vs live H-STAG

Source: `results/nano-lm/formal-htpack/formal.json`
Wall clock: 161.7s

Fit≠eval. Gate: lp ≥ STAG−ε **and** train ms/step < STAG (not e2e). Cache build reported only — ETRAIN e2e claim stays KILL.
Recipe: `seq_lo=6`, `n_stages=4`, `steps=120`, `top_k=64`, mode `PRE3 ms/step (train only) vs live STAG; not e2e`.

| family | mean teacher_lp | Δ lp | mean ms/step | Δ ms/step | mean train_wall_s | mean cache_build_s | n |
|--------|-----------------|------|--------------|-----------|------------------|--------------------|---|
| H-STAG | -13.2775 | — | 18.9 | — | 2.27 | 0.00 | 3 |
| H-TPACK | -12.4946 | +0.7828 | 14.3 | -4.6 | 1.72 | 0.65 | 3 |

**Decision:** PROMOTE (PRE3 ms/step pack vs live STAG; not e2e)

Train I/O hygiene (Wave T). Tip STAG / util PRE3 unchanged.

Commands: `npm run nano:formal:htpack` → `npm run nano:formal:htpack:report`.
