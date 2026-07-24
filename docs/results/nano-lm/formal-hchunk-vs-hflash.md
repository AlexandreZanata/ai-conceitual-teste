# Formal H-CHUNK vs H-FLASH (chunked KV prefill)

Source: `results/nano-lm/formal-hchunk/formal.json`
Wall clock: 20.0s

Shared formal B2 + formal EARLY tip. Fit≠eval (`eval_prompts`).
Long prompts + chunked KV prefill under SDPA. Kill if lp < EARLY−ε or no wall win vs H-FLASH.
Backend: `gpt_neo_sdpa + chunked KV prefill`; `chunk_size=32`; `target_tokens=128`; n_prompts=8.

| family | mean teacher_lp | Δ lp (vs EARLY) | mean wall_ms | Δ wall (vs FLASH) | mean est GFLOPs | Δ GFLOPs | n |
|--------|-----------------|-----------------|--------------|-------------------|-----------------|----------|---|
| H-EARLY | -11.8619 | — | 86 | — | 84.246 | — | 3 |
| H-FLASH | -11.8619 | — | 63 | — | 84.246 | — | 3 |
| H-CHUNK | -11.8619 | -0.0000 | 55 | -7 | 92.750 | +8.504 | 3 |

**Decision:** PROMOTE (chunked prefill under FLASH)

Note: systems util deepen on FLASH; tip EARLY genes unchanged.

Commands: `npm run nano:formal:hchunk` → `npm run nano:formal:hchunk:report`.
