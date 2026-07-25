# Formal H-HALF vs H-PRE (fp16-wire H2D under PRE)

Source: `results/nano-lm/formal-hhalf/formal.json`
Wall clock: 159.9s

Same top-k soft cache and PRE prefetch; only H2D cast path differs.
Fit≠eval. Gate: |Δlp| ≤ ε **and** train ms/step < PRE.
Recipe: `seq_lo=6`, `n_stages=4`, `steps=120`, `top_k=64`, mode `PRE prefetch; HALF keeps topk_val fp16 on H2D then GPU cast`.

| family | mean teacher_lp | Δ lp | mean ms/step | Δ ms/step | mean train_wall_s | n |
|--------|-----------------|------|--------------|-----------|------------------|---|
| H-PRE | -12.4946 | — | 14.8 | — | 1.77 | 3 |
| H-HALF | -12.4946 | +0.0000 | 14.5 | -0.3 | 1.74 | 3 |

**Decision:** PROMOTE (fp16-wire H2D under PRE)

Tip H-PRE / H-PIN util unchanged. Train I/O deepen.

Commands: `npm run nano:formal:hhalf` → `npm run nano:formal:hhalf:report`.
