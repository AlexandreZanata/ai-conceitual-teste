# H-CACHE smoke — KV cache on H-EARLY tip genes

Same EARLY tip genes on B2; decode with past_key_values.
Kill if no wall save vs EARLY or quality/B4 dual fails.

| family | mean teacher_lp | mean wall_ms | Δ lp vs EARLY | Δ lp vs B4 | n |
|--------|-----------------|--------------|---------------|------------|---|
| B4 | -17.0202 | 55 | — | — | 3 |
| H-EARLY | -16.5322 | 43 | — | — | 3 |
| H-CACHE | -16.5322 | 86 | +0.0000 | +0.4880 | 3 |

**Decision: KILL (no wall save vs H-EARLY)**

Commands: `npm run nano:cache` → `npm run nano:cache:report`.
