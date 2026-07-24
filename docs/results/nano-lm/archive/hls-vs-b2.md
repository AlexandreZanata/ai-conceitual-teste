# H-LS smoke vs B2 (label-smoothed KD)

KD with teacher soft targets mixed toward uniform: (1−ε)·q + ε/V.
Kill if ≤ B2 on teacher_lp.

| family | mean teacher_lp | Δ vs B2 | n |
|--------|-----------------|---------|---|
| B2 | -17.0918 | — | 3 |
| H-LS | -17.0918 | +0.0000 | 3 |

**Decision: KILL (≤ B2)**

Commands: `npm run nano:ls` → `npm run nano:ls:report`.
