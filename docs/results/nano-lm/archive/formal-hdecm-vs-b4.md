# Formal H-DECM vs B4 + H-LAT2 (elite gene mixture)

Source: `results/nano-lm/formal-hdecm/formal.json`
Wall clock: 58.3s

Shared B2 ckpts. LAT2 search → top-M mixture; claim on eval. Fit≠eval.
Kill if ≤ H-LAT2 or B4.

| family | mean teacher_lp | mean wall_ms | Δ lp vs B4 | n |
|--------|-----------------|--------------|------------|---|
| B4 | -14.4943 | 76 | — | 3 |
| H-LAT2 | -12.5310 | 61 | +1.9633 | 3 |
| H-DECM | -12.1956 | 241 | +2.2986 | 3 |

**Decision:** PROMOTE (mixture > H-LAT2 and B4)

Commands: `npm run nano:formal:hdecm` → `npm run nano:formal:hdecm:report`.
