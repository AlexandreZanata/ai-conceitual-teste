# H-DECM smoke vs H-LAT2 + B4 (elite gene mixture)

LAT2 search keeps top-M unique genes; claim picks completion by proxy.
Kill if ≤ H-LAT2 or B4.

| family | mean teacher_lp | mean wall_ms | Δ lp vs B4 | n |
|--------|-----------------|--------------|------------|---|
| B4 | -17.0202 | 55 | — | 3 |
| H-LAT2 | -16.6296 | 42 | +0.3906 | 3 |
| H-DECM | -16.2919 | 216 | +0.7283 | 3 |

**Decision: PROMOTE (mixture > H-LAT2 and B4)**

Commands: `npm run nano:decm` → `npm run nano:decm:report`.
