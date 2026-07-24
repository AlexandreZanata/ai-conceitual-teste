# Formal H-LAY vs H-EARLY (layer early-exit)

Source: `results/nano-lm/formal-hlay/formal.json`
Wall clock: 40.9s

Shared formal B2 + formal EARLY tip. Search max_skip/lay_conf on fit;
claim on eval_prompts. Kill if quality < EARLY−ε or no wall/GFLOPs win.

| family | mean teacher_lp | Δ lp | mean wall_ms | Δ wall | mean est GFLOPs | Δ GFLOPs | n |
|--------|-----------------|------|--------------|--------|-----------------|----------|---|
| H-EARLY | -11.8304 | — | 68 | — | 19.142 | — | 3 |
| H-LAY | -11.8304 | +0.0000 | 60 | -8 | 19.142 | +0.000 | 3 |

**Decision:** PROMOTE (layer-exit vs EARLY)

Note: on a 2-layer student, layer skip may not cut est. GFLOPs;
promote only if wall or GFLOPs dual gate is real.

Commands: `npm run nano:formal:hlay` → `npm run nano:formal:hlay:report`.
