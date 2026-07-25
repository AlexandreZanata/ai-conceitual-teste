# Formal H-QPACK — FLAYB quality pack vs H-POOL

Source: `results/nano-lm/formal-hqpack/formal.json`
Wall clock: 18.3s

Fit≠eval. Freeze FLAYB vs serial POOL (lp ≥ POOL−ε; wall↓ or tok/s↑).
n_prompts=10 chunk_size=`256` budgets=`[16, 64]` target_tokens=`128`.

| family | mean teacher_lp | Δ lp | mean tok/s | Δ tok/s | mean wall_ms | Δ wall | mean est GFLOPs | n |
|--------|-----------------|------|------------|---------|--------------|--------|-----------------|---|
| H-POOL | -12.3589 | — | 660.4 | — | 59 | — | 43.000 | 3 |
| H-FLAYB | -12.3583 | +0.0006 | 5040.7 | +4380.3 | 7 | -52 | 43.593 | 3 |

**Decision:** PROMOTE (FLAYB quality pack vs POOL)

Card hygiene (Wave T). Quality pack frozen vs tip POOL.

Commands: `npm run nano:formal:hqpack` → `npm run nano:formal:hqpack:report`.
