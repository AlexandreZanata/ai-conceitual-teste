# H-HEB smoke vs B2 (local Hebbian MLP)

KD + Hebbian update on last-layer `c_fc` (pre×post).
Kill if diverged or ≤ B2.

| family | mean teacher_lp | Δ vs B2 | n |
|--------|-----------------|---------|---|
| B2 | -17.0918 | — | 3 |
| H-HEB | -17.1104 | -0.0186 | 3 |

**Decision: KILL (≤ B2)**

Commands: `npm run nano:heb` → `npm run nano:heb:report`.
