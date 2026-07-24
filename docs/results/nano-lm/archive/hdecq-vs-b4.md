# H-DECQ smoke vs H-DECM + B4 (quantized gene codes)

Discrete temperature/top_p codebook; same elite-mixture claim as H-DECM.
Kill if ≤ H-DECM or B4.

| family | mean teacher_lp | mean wall_ms | Δ lp vs B4 | n |
|--------|-----------------|--------------|------------|---|
| B4 | -17.0202 | 55 | — | 3 |
| H-DECM | -16.2919 | 215 | +0.7283 | 3 |
| H-DECQ | -16.2025 | 170 | +0.8178 | 3 |

**Decision: PROMOTE (quantized mixture > H-DECM and B4)**

Commands: `npm run nano:decq` → `npm run nano:decq:report`.
