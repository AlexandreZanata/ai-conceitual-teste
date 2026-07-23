# Formal H-LAT2 vs B4 (λ≥0.4 + n≤2 clamp)

Source: `results/nano-lm/formal-hlat2/formal.json`
Wall clock: 55.0s

Shared B2 ckpts. pop=8 gens=12. Fit≠eval. Kill if no wall win vs B4.

| family | mean teacher_lp | mean wall_ms | Δ lp vs B4 | n |
|--------|-----------------|--------------|------------|---|
| B4 | -14.4943 | 80 | — | 3 |
| H-LAT2 | -12.1019 | 66 | +2.3923 | 3 |

**Decision:** PROMOTE (quality@wall vs B4)

Commands: `npm run nano:formal:hlat2` → `npm run nano:formal:hlat2:report`.
