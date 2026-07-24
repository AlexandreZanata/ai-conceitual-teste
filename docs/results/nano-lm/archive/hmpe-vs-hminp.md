# H-MPE smoke vs H-MINP (evolved min_p gene)

Evolve min_p + T/top_p with latency-aware fitness; claim vs grid H-MINP.
Kill if quality < tip−ε or no wall win vs H-MINP.

| family | mean teacher_lp | mean wall_ms | Δ lp vs tip | n |
|--------|-----------------|--------------|-------------|---|
| H-MINP | -16.4875 | 43 | — | 3 |
| H-MPE | -16.0363 | 43 | +0.4513 | 3 |

**Decision: PROMOTE (quality@wall vs H-MINP)**

Commands: `npm run nano:mpe` → `npm run nano:mpe:report`.
