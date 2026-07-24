# H-ALT smoke — alternate full vs shallow depth under EARLY

Search `alt_period` / `start_shallow` / `shallow_skip` with frozen EARLY tip.
Kill if lp < EARLY−ε or no wall/GFLOPs win vs EARLY.
Search λ=0.4 (FLOP-aware).

| family | mean teacher_lp | Δ lp | mean wall_ms | Δ wall | mean est GFLOPs | Δ GFLOPs | n |
|--------|-----------------|------|--------------|--------|-----------------|----------|---|
| H-EARLY | -16.8224 | — | 44 | — | 8.930 | — | 3 |
| H-ALT | -16.9841 | -0.1617 | 36 | -8 | 6.698 | -2.233 | 3 |

**Decision: KILL (quality drop vs H-EARLY)**

Note: orthogonal to conf-gated H-LAY; forced shallow on alternate steps.
Lesson: wall/GFLOPs↓ but mean teacher_lp fell below EARLY−ε (forced shallow tax).

Commands: `npm run nano:alt` → `npm run nano:alt:report`.
