# H-TMN smoke vs H-TYP × H-MINP (tip stack)

Compose tip typ_mass + tip min_p in one AR decode; dual vs max tip.
Kill if lp < max(tips)−ε or wall ≥ min(tips).

| family | mean teacher_lp | mean wall_ms | Δ lp vs max tip | n |
|--------|-----------------|--------------|-----------------|---|
| H-TYP | -16.5409 | 45 | — | 3 |
| H-MINP | -16.4875 | 43 | — | 3 |
| H-TMN | -16.5409 | 82 | -0.0533 | 3 |

**Decision: KILL (≤ max tip quality)**

Commands: `npm run nano:tmn` → `npm run nano:tmn:report`.
