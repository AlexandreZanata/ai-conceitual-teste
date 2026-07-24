# H-POOL2 smoke — tighter pop×gens vs H-POOL tip

Warm-start uses elite-biased `warm_start_pop2`; smoke budget 2×1
(tip H-POOL is 4×2). Kill if quality < POOL−ε or no fit-fwd save.

| family | mean teacher_lp | Δ vs POOL | mean wall_ms | mean fit teacher_fwd | n |
|--------|-----------------|-----------|--------------|----------------------|---|
| H-POOL | -15.5365 | — | 44 | 4 | 3 |
| H-POOL2 | -16.5933 | -1.0568 | 48 | 2 | 3 |

**Decision: KILL (quality drop vs H-POOL)**

Commands: `npm run nano:pool2` → `npm run nano:pool2:report`.
