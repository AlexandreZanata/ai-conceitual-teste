# H-TYP smoke vs B4 (typical sampling)

Grid-search typical mass on B2 student; claim best on smoke prompts.
Kill if quality < B4−ε or no wall win vs B4.

| family | mean teacher_lp | mean wall_ms | Δ lp vs B4 | n |
|--------|-----------------|--------------|------------|---|
| B4 | -17.0202 | 55 | — | 3 |
| H-TYP | -16.5409 | 45 | +0.4794 | 3 |

**Decision: PROMOTE (quality@wall vs B4)**

Commands: `npm run nano:typ` → `npm run nano:typ:report`.
