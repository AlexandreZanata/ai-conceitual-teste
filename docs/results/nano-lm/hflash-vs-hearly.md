# H-FLASH smoke — SDPA backend vs eager H-EARLY

Same EARLY tip genes; GPT-Neo `_attn` routed through `scaled_dot_product_attention` (scale=1 to match eager).
Kill if lp < EARLY−ε or no wall win. Est. GFLOPs may tie (same matmuls).
Backend: `gpt_neo_sdpa`.

| family | mean teacher_lp | Δ lp | mean wall_ms | Δ wall | mean est GFLOPs | Δ GFLOPs | n |
|--------|-----------------|------|--------------|--------|-----------------|----------|---|
| H-EARLY | -16.6154 | — | 76 | — | 8.930 | — | 3 |
| H-FLASH | -16.6139 | +0.0015 | 35 | -42 | 8.930 | +0.000 | 3 |

**Decision: PROMOTE (SDPA backend vs EARLY)**

Note: systems util; tip EARLY genes unchanged.

Commands: `npm run nano:flash` → `npm run nano:flash:report`.
