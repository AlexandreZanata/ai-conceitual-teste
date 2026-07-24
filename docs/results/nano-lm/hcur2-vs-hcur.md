# H-CUR2 smoke — n_stages ∈ {2,3,4,5} vs H-CUR (n=3)

Equal KD steps; only curriculum stage count varies.
Kill if best n ≤ H-CUR (n=3).

| n_stages | mean teacher_lp | Δ vs n=3 | n |
|----------|-----------------|----------|---|
| 2 | -16.8028 | +0.3063 | 3 |
| 3 | -17.1091 | — | 3 |
| 4 | -17.0124 | +0.0967 | 3 |
| 5 | -16.8949 | +0.2142 | 3 |

**Decision: PROMOTE (best n_stages=2 > H-CUR)**

Best n_stages: 2.

Commands: `npm run nano:cur2` → `npm run nano:cur2:report`.
