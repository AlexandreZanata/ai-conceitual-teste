# H-PROXY2 smoke vs H-DECK (CE proxy vs self-lp)

Equal pop×gens×top_k=1. Proxy: teacher-forced CE on prompt+completion
vs sampling self-lp. Kill if ≤ H-DECK quality@forwards.

| family | mean teacher_lp | Δ vs H-DECK | mean teacher_fwd | n |
|--------|-----------------|-------------|------------------|---|
| H-DECK | -16.6512 | — | 4 | 3 |
| H-PROXY2 | -16.6017 | +0.0495 | 4 | 3 |

**Decision: PROMOTE (quality@forwards vs H-DECK)**

Commands: `npm run nano:proxy2` → `npm run nano:proxy2:report`.
