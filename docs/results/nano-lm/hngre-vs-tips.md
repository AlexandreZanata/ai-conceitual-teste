# H-NGRE smoke vs H-NGRAM × H-EARLY (tip stack)

Compose tip EARLY gene + tip NGRAM size in one decode; dual vs max tip.
Kill if lp < max(tips)−ε or wall ≥ min(tips).

| family | mean teacher_lp | mean wall_ms | Δ lp vs max tip | n |
|--------|-----------------|--------------|-----------------|---|
| H-NGRAM | -16.4875 | 44 | — | 3 |
| H-EARLY | -16.5322 | 43 | — | 3 |
| H-NGRE | -16.5322 | 82 | -0.0446 | 3 |

**Decision: KILL (no dual wall win)**

Commands: `npm run nano:ngre` → `npm run nano:ngre:report`.
