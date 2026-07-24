# H-TKD smoke vs B2 (top-k sparse KD)

KD with teacher soft targets restricted to top-k (renormalized).
Kill if ≤ B2 on teacher_lp.

| family | mean teacher_lp | Δ vs B2 | n |
|--------|-----------------|---------|---|
| B2 | -17.0918 | — | 3 |
| H-TKD | -16.9119 | +0.1799 | 3 |

**Decision: PROMOTE (beats B2)**

Commands: `npm run nano:tkd` → `npm run nano:tkd:report`.
