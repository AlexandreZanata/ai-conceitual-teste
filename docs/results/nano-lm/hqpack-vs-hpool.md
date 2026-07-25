# H-QPACK smoke — FLAYB quality pack vs tip H-POOL

Card hygiene (quality axis): freeze FLAYB against serial POOL on shared budgets. Kill if lp < POOL−ε or no wall/tok/s win.
Prompt pack: `n_prompts=4`; budgets=`[16, 64]` chunk=`256` target_tokens=`128`; mode `FLAYB quality pack vs serial POOL`.

| family | mean teacher_lp | Δ lp | mean tok/s | Δ tok/s | mean wall_ms | Δ wall | mean est GFLOPs | n |
|--------|-----------------|------|------------|---------|--------------|--------|-----------------|---|
| H-POOL | -10.4879 | — | 631.7 | — | 64 | — | 42.987 | 3 |
| H-FLAYB | -10.4872 | +0.0007 | 2545.0 | +1913.3 | 15 | -49 | 43.431 | 3 |

**Decision: PROMOTE (FLAYB quality pack vs POOL)**

Tip H-POOL unchanged. Quality pack: FLAYB.

Commands: `npm run nano:qpack` → `npm run nano:qpack:report`.
