# H-EXIT smoke — earlier min_new + n=1 vs H-EARLY

min_new codebook (2,4,8); n forced to 1; FLOP-aware search.
Kill if quality < EARLY−ε or est_gflops ≥ EARLY tip.

| family | mean teacher_lp | Δ lp | mean wall_ms | mean est GFLOPs | Δ GFLOPs | n |
|--------|-----------------|------|--------------|-----------------|----------|---|
| H-EARLY | -16.5322 | — | 89 | 8.930 | — | 3 |
| H-EXIT | -16.9756 | -0.4434 | 42 | 6.751 | -2.179 | 3 |

**Decision: KILL (quality drop vs H-EARLY)**

Commands: `npm run nano:exit` → `npm run nano:exit:report`.
