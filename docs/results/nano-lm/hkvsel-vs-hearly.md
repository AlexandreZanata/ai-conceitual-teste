# H-KVSEL smoke — gated KV vs eager H-EARLY

Same EARLY tip genes; `past_key_values` only when `max_new > kv_threshold`.
Dual-budget mean over `[16, 64]`; threshold grid `[0, 16, 32, 48]`.
Kill if lp < EARLY−ε or no wall win. Prior global H-CACHE: wall↑ (archive).

| family | mean teacher_lp | Δ lp | mean wall_ms | Δ wall | mean est GFLOPs | Δ GFLOPs | n |
|--------|-----------------|------|--------------|--------|-----------------|----------|---|
| H-EARLY | -16.5322 | — | 88 | — | 15.164 | — | 3 |
| H-KVSEL | -16.5322 | +0.0000 | 55 | -33 | 1.524 | -13.640 | 3 |

Selected `kv_threshold` per seed: `[48, 48, 48]`.

**Decision: PROMOTE (gated KV vs EARLY)**

Note: systems util; tip EARLY genes unchanged aside from threshold gene.

Commands: `npm run nano:kvsel` → `npm run nano:kvsel:report`.
