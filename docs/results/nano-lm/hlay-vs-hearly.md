# H-LAY smoke — layer early-exit vs H-EARLY

Skip last *k* transformer blocks when mid-depth conf is high (frozen EARLY tip).
Kill if quality < EARLY−ε or no wall/GFLOPs win vs EARLY.

| family | mean teacher_lp | Δ lp | mean wall_ms | Δ wall | mean est GFLOPs | Δ GFLOPs | n |
|--------|-----------------|------|--------------|--------|-----------------|----------|---|
| H-EARLY | -16.5322 | — | 48 | — | 8.930 | — | 3 |
| H-LAY | -16.5322 | +0.0000 | 40 | -8 | 8.930 | +0.000 | 3 |

**Decision: PROMOTE (layer-exit vs EARLY)**

Note: est. GFLOPs may tie tip when mid-depth conf rarely clears `lay_conf`
on the 2-layer student. Formal only if FLOP/wall dual gate looks real.

Commands: `npm run nano:lay` → `npm run nano:lay:report`.
