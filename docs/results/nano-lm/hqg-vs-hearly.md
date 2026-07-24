# H-QG smoke — quality-gated FLOP min vs H-EARLY

Hard reject lp < tip−ε on fit; among survivors minimize est. GFLOPs.
Kill if empty gated set, quality < EARLY−ε, or est_gflops ≥ EARLY tip.

| family | mean teacher_lp | Δ lp | mean wall_ms | mean est GFLOPs | Δ GFLOPs | empty_rate | n |
|--------|-----------------|------|--------------|-----------------|----------|------------|---|
| H-EARLY | -16.5322 | — | 73 | 8.930 | — | 0.00 | 3 |
| H-QG | -16.8915 | -0.3593 | 40 | 6.751 | -2.179 | 0.17 | 3 |

**Decision: KILL (quality drop vs H-EARLY)**

Commands: `npm run nano:qg` → `npm run nano:qg:report`.
