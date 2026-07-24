# H-CAP smoke — hard max_new/n caps on H-POOL tip genes

Freeze POOL tip; search max_new∈{8,12,16} with n≤2; claim best lat score.
Kill if quality < POOL−ε or no wall save vs H-POOL.

| family | mean teacher_lp | mean wall_ms | Δ lp vs POOL | n |
|--------|-----------------|--------------|--------------|---|
| H-POOL | -15.5365 | 44 | — | 3 |
| H-CAP | -16.2235 | 14 | -0.6870 | 3 |

**Decision: KILL (quality < POOL−ε)**

Commands: `npm run nano:cap` → `npm run nano:cap:report`.
