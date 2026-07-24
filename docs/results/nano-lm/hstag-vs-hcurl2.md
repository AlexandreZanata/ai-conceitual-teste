# H-STAG smoke — n_stages ∈ {2,3,4} under seq_lo=6

Equal KD steps; seq_lo=6 fixed; only n_stages varies.
Kill if best n_stages ≤ H-CURL2 tip (stages=3).

| n_stages | mean teacher_lp | Δ vs stages=3 | n |
|----------|-----------------|---------------|---|
| 2 | -16.7303 | +0.5015 | 3 |
| 3 | -17.2317 | — | 3 |
| 4 | -17.0087 | +0.2231 | 3 |

**Decision: PROMOTE (best n_stages=2 > H-CURL2 tip)**

Best n_stages: 2.

Commands: `npm run nano:stag` → `npm run nano:stag:report`.
