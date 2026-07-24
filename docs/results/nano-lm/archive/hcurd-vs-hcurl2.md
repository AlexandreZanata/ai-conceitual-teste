# H-CURD smoke — teacher-NLL difficulty curriculum vs H-CURL2

Fixed seq_len (xor length curriculum); stages open easiest→hardest
by teacher CE/NLL. Equal KD steps vs tip lo=6.
Kill if ≤ H-CURL2 tip on teacher_lp.

| family | mean teacher_lp | Δ vs CURL2 | mean wall_ms | n |
|--------|-----------------|------------|--------------|---|
| H-CURL2 | -17.2317 | — | 71 | 3 |
| H-CURD | -17.2253 | +0.0064 | 39 | 3 |

**Decision: PROMOTE (beats H-CURL2 tip)**

Commands: `npm run nano:curd` → `npm run nano:curd:report`.
