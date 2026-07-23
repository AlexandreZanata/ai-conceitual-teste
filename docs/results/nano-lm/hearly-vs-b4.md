# H-EARLY smoke vs B4 (confidence early-exit)

Evolve min_new/patience/conf + n≤2; stop when confident streak.
Kill if quality < B4−ε or no wall win vs B4.

| family | mean teacher_lp | mean wall_ms | Δ lp vs B4 | n |
|--------|-----------------|--------------|------------|---|
| B4 | -17.0202 | 55 | — | 3 |
| H-EARLY | -16.5322 | 43 | +0.4880 | 3 |

**Decision: PROMOTE (quality@wall vs B4)**

Δ H-EARLY vs B4 lp: +0.4880.

Commands: `npm run nano:early` → `npm run nano:early:report`.
