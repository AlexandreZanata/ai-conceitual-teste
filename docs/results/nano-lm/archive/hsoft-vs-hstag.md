# H-SOFT smoke — offline soft-label cache vs live STAG

Precompute teacher logits once; STAG curriculum train reads cache only.
Kill if quality < STAG−ε or no train ms/step win (cache build excluded).
Recipe: `seq_lo=6`, `n_stages=4`, `steps=30`.

| family | mean teacher_lp | Δ lp | mean ms/step | Δ ms/step | mean train_wall_s | mean cache_build_s | n |
|--------|-----------------|------|--------------|-----------|------------------|--------------------|---|
| H-STAG | -17.0534 | — | 8.6 | — | 0.26 | — | 3 |
| H-SOFT | -17.0534 | +0.0000 | 10.5 | +1.9 | 0.32 | 0.21 | 3 |

**Decision: KILL (no train step-time win vs live STAG)**

Note: claim is train efficiency, not decode wall/GFLOPs.
Full-vocab soft logits over PCIe can lose to an in-GPU teacher forward on short T.

Commands: `npm run nano:soft` → `npm run nano:soft:report`.
