# H-REP smoke vs B4 (repetition-penalty decode)

Grid-search HF-style rep penalty on B2 student; claim best on smoke prompts.
Kill if quality < B4−ε or no wall win vs B4.

| family | mean teacher_lp | mean wall_ms | Δ lp vs B4 | n |
|--------|-----------------|--------------|------------|---|
| B4 | -17.0202 | 55 | — | 3 |
| H-REP | -16.4875 | 64 | +0.5327 | 3 |

**Decision: KILL (no speedup vs B4)**

Commands: `npm run nano:rep` → `npm run nano:rep:report`.
