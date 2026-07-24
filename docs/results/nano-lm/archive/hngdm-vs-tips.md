# H-NGDM smoke vs H-NGRAM × H-DECM (tip stack)

Compose tip DECM gene (BoN n/T/top_p) + tip NGRAM size; dual vs max tip.
Kill if lp < max(tips)−ε or wall ≥ min(tips).

| family | mean teacher_lp | mean wall_ms | Δ lp vs max tip | n |
|--------|-----------------|--------------|-----------------|---|
| H-NGRAM | -16.4875 | 44 | — | 3 |
| H-DECM | -16.2919 | 216 | — | 3 |
| H-NGDM | -16.3238 | 83 | -0.0319 | 3 |

**Decision: KILL (no dual wall win)**

Commands: `npm run nano:ngdm` → `npm run nano:ngdm:report`.
