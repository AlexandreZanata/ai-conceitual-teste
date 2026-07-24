# H-TOP smoke — top-k soft-label cache vs live STAG

Store teacher top-64 logits offline; STAG curriculum trains from cache.
Kill if quality < STAG−ε or no train ms/step win (cache build excluded).
Recipe: `seq_lo=6`, `n_stages=4`, `steps=30`.

| family | mean teacher_lp | Δ lp | mean ms/step | Δ ms/step | mean train_wall_s | mean cache_build_s | n |
|--------|-----------------|------|--------------|-----------|------------------|--------------------|---|
| H-STAG | -17.0327 | — | 8.9 | — | 0.27 | — | 3 |
| H-TOP | -16.6988 | +0.3340 | 5.9 | -3.0 | 0.18 | 0.16 | 3 |

**Decision: PROMOTE (top-k soft cache vs live STAG)**

Note: claim is train efficiency (not decode). Fixes H-SOFT full-vocab H2D.

Commands: `npm run nano:top` → `npm run nano:top:report`.
