# H-CURL2 smoke — fine seq_lo ∈ {4,6,8,10,12} vs tip lo=8

Equal KD steps; n_stages=3 fixed; only seq_lo varies.
Kill if best seq_lo ≤ H-CURL tip (lo=8).

| seq_lo | mean teacher_lp | Δ vs lo=8 | n |
|--------|-----------------|-----------|---|
| 4 | -16.6703 | +0.0457 | 3 |
| 6 | -17.2317 | -0.5157 | 3 |
| 8 | -16.7160 | — | 3 |
| 10 | -17.0430 | -0.3270 | 3 |
| 12 | -16.6060 | +0.1100 | 3 |

**Decision: PROMOTE (best seq_lo=12 > H-CURL tip)**

Best seq_lo: 12.

Commands: `npm run nano:curl2` → `npm run nano:curl2:report`.
