# H-ETRAIN smoke — PRE3 e2e (cache+train) vs live H-STAG

Live H-STAG e2e = train wall only (teacher forwards inside steps). H-ETRAIN e2e = top-k cache_build + PRE3 train (HALF+ADAMF+depth=3). Kill if quality < STAG−ε or no end-to-end wall win.
Recipe: `seq_lo=6`, `n_stages=4`, `steps=30`, `top_k=64`, mode `PRE3 e2e (cache_build+train) vs live STAG`.

| family | mean teacher_lp | Δ lp | mean e2e_wall_s | Δ e2e | mean ms/step | mean train_wall_s | mean cache_build_s | n |
|--------|-----------------|------|-----------------|-------|--------------|-------------------|--------------------|---|
| H-STAG | -17.0327 | — | 0.357 | — | 11.9 | 0.36 | 0.00 | 3 |
| H-ETRAIN | -16.6988 | +0.3340 | 0.258 | -0.099 | 5.7 | 0.17 | 0.09 | 3 |

**Decision: PROMOTE (PRE3 e2e vs live STAG)**

Tip H-STAG / H-PRE3 util unchanged unless PROMOTE. Full-stack train claim.

Commands: `npm run nano:etrain` → `npm run nano:etrain:report`.
