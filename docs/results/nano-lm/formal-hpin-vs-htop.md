# Formal H-PIN vs H-TOP (pinned + non_blocking H2D)

Source: `results/nano-lm/formal-hpin/formal.json`
Wall clock: 163.5s

Same top-k soft cache and STAG curriculum; only H2D path differs.
Fit≠eval. Gate: lp ≥ TOP−ε **and** train ms/step < TOP.
Recipe: `seq_lo=6`, `n_stages=4`, `steps=120`, `top_k=64`, mode `pin_memory + non_blocking H2D`.

| family | mean teacher_lp | Δ lp | mean ms/step | Δ ms/step | mean train_wall_s | n |
|--------|-----------------|------|--------------|-----------|------------------|---|
| H-TOP | -12.4946 | — | 14.8 | — | 1.78 | 3 |
| H-PIN | -12.4946 | +0.0000 | 14.5 | -0.3 | 1.74 | 3 |

**Decision:** PROMOTE (pinned H2D vs TOP)

Tip H-TOP util unchanged; H-PIN is train I/O deepen.

Commands: `npm run nano:formal:hpin` → `npm run nano:formal:hpin:report`.
