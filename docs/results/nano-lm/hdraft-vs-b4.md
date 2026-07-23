# H-DRAFT smoke vs B4 (evolved speculative draft knobs)

Evolve draft_len∈{1,2,4,8} + temp/top_p; student draft, teacher verify.
Kill if quality < B4−ε or no wall win vs B4 (distinct from H-SPEC vs B3).

| family | mean teacher_lp | mean wall_ms | Δ lp vs B4 | n |
|--------|-----------------|--------------|------------|---|
| B4 | -17.0202 | 55 | — | 3 |
| H-SPEC | -1.3358 | 239 | +15.6845 | 3 |
| H-DRAFT | -1.6295 | 321 | +15.3908 | 3 |

**Decision: KILL (no speedup vs B4)**

Δ H-DRAFT vs B4 lp: +15.3908.

Commands: `npm run nano:draft` → `npm run nano:draft:report`.
