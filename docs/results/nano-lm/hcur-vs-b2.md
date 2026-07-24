# H-CUR smoke vs B2 (length-curriculum KD)

KD with 3-stage seq_len ramp short→full; equal steps vs fixed-seq B2.
Kill if ≤ B2 on teacher_lp.

| family | mean teacher_lp | Δ vs B2 | n |
|--------|-----------------|---------|---|
| B2 | -17.0918 | — | 3 |
| H-CUR | -17.0133 | +0.0785 | 3 |

**Decision: PROMOTE (beats B2)**

Commands: `npm run nano:cur` → `npm run nano:cur:report`.
