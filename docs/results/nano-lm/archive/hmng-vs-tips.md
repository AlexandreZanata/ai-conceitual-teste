# H-MNG smoke vs H-MINP × H-NGRAM (tip stack)

Compose tip min_p + tip ngram_size in one AR decode; dual vs max tip.
Kill if lp < max(tips)−ε or wall ≥ min(tips).

| family | mean teacher_lp | mean wall_ms | Δ lp vs max tip | n |
|--------|-----------------|--------------|-----------------|---|
| H-MINP | -16.4875 | 43 | — | 3 |
| H-NGRAM | -16.4875 | 44 | — | 3 |
| H-MNG | -16.4875 | 77 | +0.0000 | 3 |

**Decision: KILL (no dual wall win)**

Commands: `npm run nano:mng` → `npm run nano:mng:report`.
