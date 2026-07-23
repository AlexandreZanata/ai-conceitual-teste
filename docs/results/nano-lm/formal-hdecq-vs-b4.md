# Formal H-DECQ vs B4 + H-DECM (quantized gene codes)

Source: `results/nano-lm/formal-hdecq/formal.json`
Wall clock: 162.8s

Shared B2 ckpts. Discrete T/top_p codebook; mixture claim. Fit≠eval.
Kill if ≤ H-DECM or B4.

| family | mean teacher_lp | mean wall_ms | Δ lp vs B4 | n |
|--------|-----------------|--------------|------------|---|
| B4 | -14.4943 | 148 | — | 3 |
| H-DECM | -12.3313 | 261 | +2.1629 | 3 |
| H-DECQ | -13.2003 | 424 | +1.2940 | 3 |

**Decision:** KILL (≤ H-DECM)

Commands: `npm run nano:formal:hdecq` → `npm run nano:formal:hdecq:report`.
