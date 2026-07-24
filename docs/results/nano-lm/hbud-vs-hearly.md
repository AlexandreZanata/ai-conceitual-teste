# H-BUD smoke — EARLY exit + max_new as one gene

Warm-start from EARLY tip; co-evolve max_new with exit knobs.
Kill if dominated by H-EARLY on (lp, wall) or quality < EARLY−ε.

| family | mean teacher_lp | mean wall_ms | Δ lp vs EARLY | n |
|--------|-----------------|--------------|---------------|---|
| H-EARLY | -16.5322 | 43 | — | 3 |
| H-BUD | -17.1662 | 22 | -0.6341 | 3 |

**Decision: KILL (quality drop vs H-EARLY)**

Commands: `npm run nano:bud` → `npm run nano:bud:report`.
