# H-TPACK smoke — PRE3 ms/step pack vs live H-STAG

Train I/O card hygiene: gate on **ms/step only** (not e2e). Live STAG = teacher-in-loop train; TPACK = top-k cache + PRE3 train. Cache build is reported but not gated (ETRAIN e2e claim stays KILL). Kill if lp < STAG−ε or no ms/step win.
Recipe: `seq_lo=6`, `n_stages=4`, `steps=30`, `top_k=64`, mode `PRE3 ms/step (train only) vs live STAG; not e2e`.

| family | mean teacher_lp | Δ lp | mean ms/step | Δ ms/step | mean train_wall_s | mean cache_build_s | n |
|--------|-----------------|------|--------------|-----------|------------------|--------------------|---|
| H-STAG | -17.0327 | — | 11.4 | — | 0.34 | 0.00 | 3 |
| H-TPACK | -16.6988 | +0.3340 | 5.6 | -5.8 | 0.17 | 0.08 | 3 |

**Decision: PROMOTE (PRE3 ms/step pack vs live STAG; not e2e)**

Tip H-STAG / util H-PRE3 unchanged. Do not reopen ETRAIN e2e claim.

Commands: `npm run nano:tpack` → `npm run nano:tpack:report`.
