# Formal H-POOLF vs H-POOL (FLOP-aware n≤2)

Source: `results/nano-lm/formal-hpoolf/formal.json`
Wall clock: 56.6s

Fit≠eval; n≤2 + POOL tip warm-start; score = lp − λ·log1p(GFLOPs).
Kill if lp < POOL−ε or est_gflops ≥ POOL tip.

| family | mean teacher_lp | Δ lp | mean wall_ms | mean est GFLOPs | Δ GFLOPs | n |
|--------|-----------------|------|--------------|-----------------|----------|---|
| H-POOL | -11.6938 | — | 83 | 49.631 | — | 3 |
| H-POOLF | -11.9637 | -0.2699 | 64 | 15.378 | -34.253 | 3 |

**Decision:** KILL (quality drop vs H-POOL)

Commands: `npm run nano:formal:hpoolf` → `npm run nano:formal:hpoolf:report`.
