# Formal H-Q4 vs H-DEPTH (CUDA int4 weight-only)

Source: `results/nano-lm/formal-hq4/formal.json`
Wall clock: 7.1s

Formal `HDEPTH_prun` + formal EARLY tip. Fit≠eval (`eval_prompts`).
Weight-only int4 via `aten::_weight_int4pack_mm`. Kill if lp < DEPTH−ε or no wall win.
Backend: `aten_int4pack_cuda`; `groupsize=32`; `tiles=2`; n_prompts=8.

| family | mean teacher_lp | Δ lp | mean wall_ms | Δ wall | mean est GFLOPs | Δ GFLOPs | mean weight_bytes | Δ bytes | n |
|--------|-----------------|------|--------------|--------|-----------------|----------|-------------------|--------|---|
| H-DEPTH | -8.2350 | — | 46 | — | 18.016 | — | 13458692 | — | 3 |
| H-Q4 | -8.4293 | -0.1943 | 43 | -3 | 17.290 | -0.727 | 13292036 | -166656 | 3 |

**Decision:** KILL (quality drop vs H-DEPTH)

Note: systems util on DEPTH ckpt; tip genes unchanged.

Commands: `npm run nano:formal:hq4` → `npm run nano:formal:hq4:report`.
