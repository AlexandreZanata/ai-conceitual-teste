# H-LAT smoke vs B4 (latency-aware decode genes)

Fitness during search: `lp − λ·log1p(wall_ms)` on frozen B2 student.
Claim metric: raw teacher_lp + mean_wall_ms on eval prompts.

| family | mean teacher_lp | mean wall_ms | Δ lp vs B4 | n |
|--------|-----------------|--------------|------------|---|
| B4 | -17.0202 | 55 | — | 3 |
| H-DEC | -16.9235 | — | +0.0967 | 3 |
| H-LAT | -16.7523 | 135 | +0.2679 | 3 |

**Decision: KILL (no speedup vs B4)**

Δ H-LAT vs B4 lp: +0.2679.
H-DEC present: lp=-16.9235.

Commands: `npm run nano:lat` → `npm run nano:matrix:report`.
