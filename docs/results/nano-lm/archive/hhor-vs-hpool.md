# H-HOR smoke — freeze tip n + horizon≤2 + FLOP vs H-POOL

Preserve tip BoN width `n`; clamp MAE horizon ≤ 2; FLOP-aware score.
Kill if quality < POOL−ε or est_gflops ≥ POOL tip.

| family | mean teacher_lp | Δ lp | mean wall_ms | mean est GFLOPs | Δ GFLOPs | n |
|--------|-----------------|------|--------------|-----------------|----------|---|
| H-POOL | -16.2184 | — | 77 | 17.718 | — | 3 |
| H-HOR | -16.1400 | +0.0785 | 43 | 17.718 | +0.000 | 3 |

**Decision: KILL (no FLOP win vs H-POOL)**

Commands: `npm run nano:hor` → `npm run nano:hor:report`.
