# H-CHUNK smoke — chunked KV prefill under FLASH

Same EARLY tip genes; long prompts (`target_tokens`); prefill in blocks of `chunk_size` under SDPA + KV, then generate.
Kill if lp < EARLY−ε or no wall win vs H-FLASH.
Backend: `gpt_neo_sdpa + chunked KV prefill`; `chunk_size=32`; `target_tokens=128`.

| family | mean teacher_lp | Δ lp (vs EARLY) | mean wall_ms | Δ wall (vs FLASH) | mean est GFLOPs | Δ GFLOPs | n |
|--------|-----------------|-----------------|--------------|-------------------|-----------------|----------|---|
| H-EARLY | -16.7587 | — | 81 | — | 42.938 | — | 3 |
| H-FLASH | -16.7597 | — | 39 | — | 42.938 | — | 3 |
| H-CHUNK | -16.7597 | -0.0010 | 37 | -2 | 48.921 | +5.983 | 3 |

**Decision: PROMOTE (chunked prefill under FLASH)**

Note: systems util deepen on FLASH; tip EARLY genes unchanged.

Commands: `npm run nano:chunk` → `npm run nano:chunk:report`.
