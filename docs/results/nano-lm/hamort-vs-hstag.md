# H-AMORT smoke — amortized soft-cache e2e vs live H-STAG

New e2e story without ASYNC: build top-k soft-cache **once**, run **n=4** PRE3 trains on the same cache. Amortized e2e = cache_build/n + mean(PRE3 train wall). Live STAG e2e = train wall only. Kill if lp < STAG−ε or amortized e2e ≥ live.
Mode: `cache once + n=4 PRE3; amortized e2e vs live STAG`; seq_lo=`6` n_stages=`4` steps=`30` top_k=`64`.

| family | mean teacher_lp | Δ lp | mean e2e_wall_s | Δ e2e |
|--------|-----------------|------|-----------------|-------|
| H-STAG (live) | -17.0327 | — | 0.334 | — |
| H-AMORT | -16.8908 | +0.1419 | 0.188 | -0.146 |

**Decision: PROMOTE (amortized e2e over n=4 PRE3 runs)**

Tip H-STAG / util H-PRE3 unchanged. Reopens e2e claim with amortization (ETRAIN N=1 stays KILL).

| seed | cache_s | mean PRE3 train_s | amort e2e | live e2e |
|------|---------|-------------------|-----------|----------|
| 0 | 0.090 | 0.167 | 0.189 | 0.527 |
| 1 | 0.074 | 0.170 | 0.189 | 0.235 |
| 2 | 0.075 | 0.168 | 0.187 | 0.240 |

Commands: `npm run nano:amort` → `npm run nano:amort:report`.
