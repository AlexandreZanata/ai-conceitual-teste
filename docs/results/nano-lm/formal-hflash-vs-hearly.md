# Formal H-FLASH vs H-EARLY (SDPA attention backend)

Source: `results/nano-lm/formal-hflash/formal.json`
Wall clock: 14.1s

Shared formal B2 + formal EARLY tip. Fit≠eval (`eval_prompts`).
GPT-Neo `_attn` → SDPA (scale=1). Kill if lp < EARLY−ε or no wall win.
Backend: `gpt_neo_sdpa`; n_prompts=8.

| family | mean teacher_lp | Δ lp | mean wall_ms | Δ wall | mean est GFLOPs | Δ GFLOPs | n |
|--------|-----------------|------|--------------|--------|-----------------|----------|---|
| H-EARLY | -11.8480 | — | 74 | — | 19.142 | — | 3 |
| H-FLASH | -11.8480 | -0.0000 | 53 | -21 | 19.142 | +0.000 | 3 |

**Decision:** PROMOTE (SDPA backend vs EARLY)

Note: systems util — tip EARLY genes unchanged; est. GFLOPs may tie.

Commands: `npm run nano:formal:hflash` → `npm run nano:formal:hflash:report`.
