# H-POOLF smoke — FLOP-aware POOL + n≤2 vs H-POOL

Warm-start from POOL tip; search score = lp − λ·log1p(GFLOPs); n clamped ≤2.
Kill if quality < POOL−ε or est_gflops ≥ POOL tip.

| family | mean teacher_lp | Δ lp | mean wall_ms | mean est GFLOPs | Δ GFLOPs | n |
|--------|-----------------|------|--------------|-----------------|----------|---|
| H-POOL | -16.2184 | — | 75 | 17.718 | — | 3 |
| H-POOLF | -15.9574 | +0.2611 | 67 | 15.503 | -2.215 | 3 |

**Decision: PROMOTE (FLOP-aware POOL vs tip)**

Commands: `npm run nano:poolf` → `npm run nano:poolf:report`.
