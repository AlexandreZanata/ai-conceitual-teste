# H-CLIP smoke vs B2 (logit-clipped KD)

KD after clamping student/teacher logits to [-clip, clip] (default 5).
Kill if ≤ B2 on teacher_lp.

| family | mean teacher_lp | Δ vs B2 | n |
|--------|-----------------|---------|---|
| B2 | -17.0918 | — | 3 |
| H-CLIP | -17.4336 | -0.3418 | 3 |

**Decision: KILL (≤ B2)**

Commands: `npm run nano:clip` → `npm run nano:clip:report`.
