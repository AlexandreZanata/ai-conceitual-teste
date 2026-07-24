# H-PROX smoke — CE-only fit proxy vs H-POOL claim

Warm-start like H-POOL; search ranks by student CE only
(no teacher forwards in fit). Claim uses full teacher_lp.
Kill if claim quality < POOL−ε.

| family | mean teacher_lp | Δ vs POOL | mean wall_ms | mean fit teacher_fwd | n |
|--------|-----------------|-----------|--------------|----------------------|---|
| H-POOL | -15.5365 | — | 44 | 4 | 3 |
| H-PROX | -15.6092 | -0.0727 | 67 | 0 | 3 |

**Decision: KILL (claim quality drop vs H-POOL)**

Commands: `npm run nano:prox` → `npm run nano:prox:report`.
