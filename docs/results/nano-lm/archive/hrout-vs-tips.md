# H-ROUT smoke vs H-EARLY × H-DECM (confidence tip router)

Route frozen tip genes by prompt-top confidence (early if conf≥τ).
Kill if ≤ max tip quality or no wall win vs faster tip.

| family | mean teacher_lp | mean wall_ms | Δ lp vs max tip | n |
|--------|-----------------|--------------|-----------------|---|
| H-EARLY | -16.5322 | 43 | — | 3 |
| H-DECM | -16.2919 | 216 | — | 3 |
| H-ROUT | -16.5836 | 61 | -0.2917 | 3 |

**Decision: KILL (≤ max tip quality)**

Commands: `npm run nano:rout` → `npm run nano:rout:report`.
