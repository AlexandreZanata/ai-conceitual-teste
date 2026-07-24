# H-LOT smoke vs B2 (sparse lottery ticket)

Warmup KD → magnitude prune → rewind to init ⊙ mask → retrain.
Kill if ≤ B2; quality cliff if Δ < −0.5.

| family | mean teacher_lp | Δ vs B2 | n |
|--------|-----------------|---------|---|
| B2 | -17.0918 | — | 3 |
| H-LOT | -16.9338 | +0.1580 | 3 |

**Decision: PROMOTE (beats B2)**

Commands: `npm run nano:lot` → `npm run nano:lot:report`.
