# H-TPE smoke vs H-TYP (evolved typ_mass gene)

Evolve typ_mass + T/top_p with latency-aware fitness; claim vs grid H-TYP.
Kill if quality < tip−ε or no wall win vs H-TYP.

| family | mean teacher_lp | mean wall_ms | Δ lp vs tip | n |
|--------|-----------------|--------------|-------------|---|
| H-TYP | -16.5409 | 45 | — | 3 |
| H-TPE | -16.6677 | 44 | -0.1269 | 3 |

**Decision: KILL (quality drop vs H-TYP)**

Commands: `npm run nano:tpe` → `npm run nano:tpe:report`.
