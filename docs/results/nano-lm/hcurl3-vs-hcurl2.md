# H-CURL3 smoke — micro seq_lo ∈ {5,6,7} vs tip lo=6

Equal KD steps; n_stages=3 fixed; only seq_lo varies.
Kill if best seq_lo ≤ H-CURL2 tip (lo=6).

| seq_lo | mean teacher_lp | Δ vs lo=6 | n |
|--------|-----------------|-----------|---|
| 5 | -17.1381 | +0.0937 | 3 |
| 6 | -17.2317 | — | 3 |
| 7 | -16.3831 | +0.8487 | 3 |

**Decision: PROMOTE (best seq_lo=7 > H-CURL2 tip)**

Best seq_lo: 7.

Commands: `npm run nano:curl3` → `npm run nano:curl3:report`.
