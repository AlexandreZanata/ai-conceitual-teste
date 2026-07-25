# Formal H-AMORT — amortized soft-cache e2e vs live H-STAG

Source: `results/nano-lm/formal-hamort/formal.json`
Wall clock: 230.4s

New e2e story without ASYNC: build top-k soft-cache **once**, run **n=4** PRE3 trains on the same cache. Amortized e2e = cache_build/n + mean(PRE3 train wall). Live STAG e2e = train wall only. Kill if lp < STAG−ε or amortized e2e ≥ live.
Mode: `cache once + n=4 PRE3; amortized e2e vs live STAG`; seq_lo=`6` n_stages=`4` steps=`120` top_k=`64`.

| family | mean teacher_lp | Δ lp | mean e2e_wall_s | Δ e2e |
|--------|-----------------|------|-----------------|-------|
| H-STAG (live) | -13.2775 | — | 2.238 | — |
| H-AMORT | -12.4072 | +0.8703 | 1.839 | -0.399 |

**Decision: PROMOTE (amortized e2e over n=4 PRE3 runs)**

Tip H-STAG / util H-PRE3 unchanged. Reopens e2e claim with amortization (ETRAIN N=1 stays KILL).

| seed | cache_s | mean PRE3 train_s | amort e2e | live e2e |
|------|---------|-------------------|-----------|----------|
| 0 | 0.635 | 1.682 | 1.841 | 2.418 |
| 1 | 0.615 | 1.680 | 1.834 | 2.168 |
| 2 | 0.618 | 1.689 | 1.843 | 2.128 |

Commands: `npm run nano:formal:hamort` → `npm run nano:formal:hamort:report`.
