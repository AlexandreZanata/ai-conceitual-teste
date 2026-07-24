# H-ALAT smoke — KD α/T schedule under CURL2 (H-αT)

Same seq_lo=6 length stages as tip; α 0.25→0.75, T 3.0→1.0 by stage.
Kill if ≤ H-CURL2 tip on teacher_lp @ equal steps.

| family | mean teacher_lp | Δ vs CURL2 | mean wall_ms | n |
|--------|-----------------|------------|--------------|---|
| H-CURL2 | -17.2317 | — | 73 | 3 |
| H-ALAT | -17.4635 | -0.2318 | 44 | 3 |

**Decision: KILL (≤ H-CURL2 tip)**

Commands: `npm run nano:alat` → `npm run nano:alat:report`.
