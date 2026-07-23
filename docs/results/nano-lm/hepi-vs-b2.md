# H-EPI smoke vs B2 (context-dependent LR/masks)

Scale LR by teacher token entropy; mask embed grads on easy batches.
Kill if ≤ fixed-LR B2.

| family | mean teacher_lp | Δ vs B2 | n |
|--------|-----------------|---------|---|
| B2 | -17.0918 | — | 3 |
| H-EPI | -17.2130 | -0.1212 | 3 |

**Decision: KILL (≤ fixed LR / B2)**

Commands: `npm run nano:epi` → `npm run nano:epi:report`.
