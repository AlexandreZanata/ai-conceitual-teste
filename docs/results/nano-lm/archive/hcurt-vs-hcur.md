# H-CURT smoke vs H-CUR (adopted tip n=5, lo=8)

Curriculum KD with n_stages=5, seq_lo=8 (formal-best knobs).
Kill if ≤ H-CUR tip (n=3, lo=16).

| family | mean teacher_lp | Δ vs tip | n |
|--------|-----------------|----------|---|
| H-CUR | -17.0133 | — | 3 |
| H-CURT | -17.0595 | -0.0461 | 3 |

**Decision: KILL (≤ H-CUR tip)**

Commands: `npm run nano:curt` → `npm run nano:curt:report`.
