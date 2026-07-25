# Formal H-PRE2 vs H-ADAMF (2-deep prefetch under ADAMF)

Source: `results/nano-lm/formal-hpre2/formal.json`
Wall clock: 158.6s

Same ADAMF I/O path; only prefetch_depth differs (2 vs 1).
Fit≠eval. Gate: |Δlp| ≤ ε **and** train ms/step < ADAMF.
Recipe: `seq_lo=6`, `n_stages=4`, `steps=120`, `top_k=64`, mode `ADAMF I/O + prefetch_depth=2 vs depth=1`.

| family | mean teacher_lp | Δ lp | mean ms/step | Δ ms/step | mean train_wall_s | n |
|--------|-----------------|------|--------------|-----------|------------------|---|
| H-ADAMF | -12.4946 | — | 14.6 | — | 1.75 | 3 |
| H-PRE2 | -12.4946 | +0.0000 | 14.3 | -0.2 | 1.72 | 3 |

**Decision:** PROMOTE (2-deep prefetch under ADAMF)

Tip H-ADAMF / H-PRE util unchanged. Train I/O deepen.

Commands: `npm run nano:formal:hpre2` → `npm run nano:formal:hpre2:report`.
