# Formal H-DEPTH vs H-STAG (1-layer STAG + PRUN)

Source: `results/nano-lm/formal-hdepth/formal.json`
Wall clock: 226.8s

Formal STAG tip control; H-DEPTH trains `n_layers=1` under STAG recipe, then mag-prune + KD recover. Fit≠eval (`eval_prompts`).
recover_steps=60; sparsity_target=0.3; n_prompts=8.
Kill if lp < STAG−ε or no wall win.

| family | mean teacher_lp | Δ lp | mean wall_ms | Δ wall | mean est GFLOPs | Δ GFLOPs | params | n |
|--------|-----------------|------|--------------|--------|-----------------|----------|--------|---|
| H-STAG | -10.7499 | — | 135 | — | 19.142 | — | 3348928 | 3 |
| H-DEPTH | -7.6405 | +3.1094 | 106 | -29 | 12.624 | -6.518 | 3299136 | 3 |

**Decision:** PROMOTE (shallow STAG+PRUN vs tip)

Note: arch depth cut ≠ H-THIN width paste; tip STAG unchanged.

Commands: `npm run nano:formal:hdepth` → `npm run nano:formal:hdepth:report`.
