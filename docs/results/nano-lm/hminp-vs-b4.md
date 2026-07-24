# H-MINP smoke vs B4 (min-p sampling)

Grid-search min_p on B2 student; claim best on smoke prompts.
Kill if quality < B4−ε or no wall win vs B4.

| family | mean teacher_lp | mean wall_ms | Δ lp vs B4 | n |
|--------|-----------------|--------------|------------|---|
| B4 | -17.0202 | 55 | — | 3 |
| H-MINP | -16.4875 | 43 | +0.5327 | 3 |

**Decision: PROMOTE (quality@wall vs B4)**

Commands: `npm run nano:minp` → `npm run nano:minp:report`.
