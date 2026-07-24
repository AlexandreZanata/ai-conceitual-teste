# Formal H-PRUN vs H-STAG (magnitude prune + recovery)

Source: `results/nano-lm/formal-hprun/formal.json`
Wall clock: 59.7s

Formal STAG tip → 30% mag prune → masked KD recovery; claim with formal EARLY.
Fit≠eval (`eval_prompts`). Formal gate: quality ≥ STAG−ε **and wall < STAG**
(density FLOPs alone are not a real dual gate under dense CUDA kernels).
recover_steps=60; sparsity_target=0.3.

| family | mean teacher_lp | Δ lp | mean wall_ms | Δ wall | mean est GFLOPs | Δ GFLOPs | density | n |
|--------|-----------------|------|--------------|--------|-----------------|----------|---------|---|
| H-STAG | -11.0923 | — | 74 | — | 19.142 | — | 1.000 | 3 |
| H-PRUN | -10.5199 | +0.5725 | 55 | -18 | 8.805 | -10.337 | 0.700 | 3 |

**Decision:** PROMOTE (prune+recover wall vs STAG)

Note: density-scaled GFLOPs remain theoretical (dense kernels still run);
formal promote requires mean wall win across seeds.

Commands: `npm run nano:formal:hprun` → `npm run nano:formal:hprun:report`.
