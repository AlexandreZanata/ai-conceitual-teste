# H-POOL3 smoke — FLOP-aware POOL + n≤3 vs H-POOL

Softens H-POOLF (n≤2→n≤3); score = lp − λ·log1p(GFLOPs); tip warm-start.
Kill if quality < POOL−ε or est_gflops ≥ POOL tip.

| family | mean teacher_lp | Δ lp | mean wall_ms | mean est GFLOPs | Δ GFLOPs | n |
|--------|-----------------|------|--------------|-----------------|----------|---|
| H-POOL | -16.2184 | — | 76 | 17.718 | — | 3 |
| H-POOL3 | -15.6759 | +0.5426 | 72 | 19.933 | +2.215 | 3 |

**Decision: KILL (no FLOP win vs H-POOL)**

Commands: `npm run nano:pool3` → `npm run nano:pool3:report`.
