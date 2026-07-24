# Formal H-KVSEL vs H-EARLY (gated KV)

Source: `results/nano-lm/formal-hkvsel/formal.json`
Wall clock: 59.3s

Shared formal B2 + formal EARLY tip. Fit≠eval (`eval_prompts`).
KV iff `max_new > kv_threshold`; dual-budget mean `[16, 64]`.
Kill if lp < EARLY−ε or no wall win.
n_prompts=8.

| family | mean teacher_lp | Δ lp | mean wall_ms | Δ wall | mean est GFLOPs | Δ GFLOPs | n |
|--------|-----------------|------|--------------|--------|-----------------|----------|---|
| H-EARLY | -12.3272 | — | 100 | — | 17.381 | — | 3 |
| H-KVSEL | -12.3284 | -0.0011 | 62 | -38 | 1.003 | -16.378 | 3 |

Selected `kv_threshold` per seed: `[0, 32, 32]`.

**Decision:** PROMOTE (gated KV vs EARLY)

Note: systems util — tip EARLY genes unchanged aside from threshold.

Commands: `npm run nano:formal:hkvsel` → `npm run nano:formal:hkvsel:report`.
