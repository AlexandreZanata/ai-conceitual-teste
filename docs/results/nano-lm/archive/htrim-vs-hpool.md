# H-TRIM smoke — freeze tip n + FLOP search vs H-POOL

Preserve tip BoN width `n`; mutate other knobs with lp − λ·log1p(GFLOPs).
Kill if quality < POOL−ε or est_gflops ≥ POOL tip.

| family | mean teacher_lp | Δ lp | mean wall_ms | mean est GFLOPs | Δ GFLOPs | n |
|--------|-----------------|------|--------------|-----------------|----------|---|
| H-POOL | -16.2184 | — | 74 | 17.718 | — | 3 |
| H-TRIM | -15.4034 | +0.8150 | 60 | 22.148 | +4.430 | 3 |

**Decision: KILL (no FLOP win vs H-POOL)**

Commands: `npm run nano:trim` → `npm run nano:trim:report`.
