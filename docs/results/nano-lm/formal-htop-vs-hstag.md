# Formal H-TOP vs live H-STAG (top-k soft-label cache)

Source: `results/nano-lm/formal-htop/formal.json`
Wall clock: 215.2s

Store teacher top-64 logits offline; STAG curriculum from cache.
Fit≠eval (`eval_prompts`). Gate: lp ≥ STAG−ε **and** train ms/step < live STAG
(cache build excluded from ms/step).
Recipe: `seq_lo=6`, `n_stages=4`, `steps=120`.

| family | mean teacher_lp | Δ lp | mean ms/step | Δ ms/step | mean train_wall_s | mean cache_build_s | n |
|--------|-----------------|------|--------------|-----------|------------------|--------------------|---|
| H-STAG | -13.2775 | — | 18.4 | — | 2.21 | — | 3 |
| H-TOP | -12.4946 | +0.7828 | 14.5 | -3.9 | 1.75 | 0.73 | 3 |

**Decision:** PROMOTE (top-k soft cache vs live STAG)

Note: claim is train efficiency (not decode). Tip H-STAG weights unchanged.

Commands: `npm run nano:formal:htop` → `npm run nano:formal:htop:report`.
