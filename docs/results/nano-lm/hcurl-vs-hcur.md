# H-CURL smoke — seq_lo ∈ {8,16,32} vs H-CUR (lo=16)

Equal KD steps; n_stages=3 fixed; only seq_lo varies.
Kill if best seq_lo ≤ H-CUR (lo=16).

| seq_lo | mean teacher_lp | Δ vs lo=16 | n |
|--------|-----------------|------------|---|
| 8 | -16.7160 | +0.1408 | 3 |
| 16 | -16.8569 | — | 3 |
| 32 | -16.4792 | +0.3777 | 3 |

**Decision: PROMOTE (best seq_lo=32 > H-CUR)**

Best seq_lo: 32.

Commands: `npm run nano:curl` → `npm run nano:curl:report`.
