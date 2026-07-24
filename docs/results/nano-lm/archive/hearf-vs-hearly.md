# H-EARF smoke — FLOP-aware early-exit vs H-EARLY

Search score = lp − λ·log1p(est GFLOPs). Same early gene space as tip.
Kill if quality < EARLY−ε or est_gflops ≥ EARLY tip.

| family | mean teacher_lp | Δ lp | mean wall_ms | mean est GFLOPs | Δ GFLOPs | n |
|--------|-----------------|------|--------------|-----------------|----------|---|
| H-EARLY | -16.5322 | — | 79 | 8.930 | — | 3 |
| H-EARF | -16.5322 | +0.0000 | 42 | 8.930 | +0.000 | 3 |

**Decision: KILL (no FLOP win vs H-EARLY)**

Commands: `npm run nano:earf` → `npm run nano:earf:report`.
