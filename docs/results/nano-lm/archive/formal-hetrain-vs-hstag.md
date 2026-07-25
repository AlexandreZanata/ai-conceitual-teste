# Formal H-ETRAIN vs H-STAG (PRE3 e2e train wall)

Source: `results/nano-lm/formal-hetrain/formal.json`
Wall clock: 167.3s

Fit≠eval. Live STAG e2e = train only; ETRAIN e2e = cache_build + PRE3 train. Gate: lp ≥ STAG−ε **and** e2e_wall < STAG.
Recipe: `seq_lo=6`, `n_stages=4`, `steps=120`, `top_k=64`, mode `PRE3 e2e (cache_build+train) vs live STAG`.

| family | mean teacher_lp | Δ lp | mean e2e_wall_s | Δ e2e | mean ms/step | mean train_wall_s | mean cache_build_s | n |
|--------|-----------------|------|-----------------|-------|--------------|-------------------|--------------------|---|
| H-STAG | -13.2775 | — | 2.283 | — | 19.0 | 2.28 | 0.00 | 3 |
| H-ETRAIN | -12.4946 | +0.7828 | 2.373 | +0.090 | 14.4 | 1.73 | 0.64 | 3 |

**Decision:** KILL (no end-to-end train wall win vs H-STAG)

Tip H-STAG / H-PRE3 util unchanged. Full-stack train claim (Wave R).

Commands: `npm run nano:formal:hetrain` → `npm run nano:formal:hetrain:report`.
