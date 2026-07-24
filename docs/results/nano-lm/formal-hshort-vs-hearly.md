# Formal H-SHORT vs H-EARLY (two-phase short draft)

Source: `results/nano-lm/formal-hshort/formal.json`
Wall clock: 43.9s

Shared formal B2 + formal EARLY tip. Search draft_max/stop_conf on fit;
claim on eval_prompts. Kill if quality < EARLY−ε or dominated on (wall, GFLOPs).

| family | mean teacher_lp | Δ lp | mean wall_ms | Δ wall | mean est GFLOPs | Δ GFLOPs | n |
|--------|-----------------|------|--------------|--------|-----------------|----------|---|
| H-EARLY | -11.8304 | — | 70 | — | 19.142 | — | 3 |
| H-SHORT | -11.8304 | +0.0000 | 66 | -3 | 19.142 | +0.000 | 3 |

**Decision:** PROMOTE (adaptive short draft vs EARLY)

Note: wall Δ remains small (~3ms) with GFLOPs tie — util only;
does not replace H-EARLY tip. Dual gate is wall-only and marginal.

Commands: `npm run nano:formal:hshort` → `npm run nano:formal:hshort:report`.
