# H-NGRAM smoke vs B4 (no-repeat n-gram decode)

Grid-search no_repeat_ngram_size on B2 student; claim best on smoke prompts.
Kill if quality < B4−ε or no wall win vs B4.

| family | mean teacher_lp | mean wall_ms | Δ lp vs B4 | n |
|--------|-----------------|--------------|------------|---|
| B4 | -17.0202 | 55 | — | 3 |
| H-NGRAM | -16.4875 | 44 | +0.5327 | 3 |

**Decision: PROMOTE (quality@wall vs B4)**

Commands: `npm run nano:ngram` → `npm run nano:ngram:report`.
