# H-CHB smoke — chunk_size sweep vs H-CHUNK tip

Same EARLY tip genes; long prompts; prefill block sizes `B∈[32, 64, 128, 256]` under SDPA+KV. Tip CHUNK uses `B=32`.
PROMOTE iff best-B lp ≥ EARLY−ε and wall < CHUNK tip; else KILL.
Backend: `gpt_neo_sdpa + chunked KV prefill sweep`; `target_tokens=128`; smoke winner `chunk_size=256`.

| family | mean teacher_lp | Δ lp (vs EARLY) | mean wall_ms | Δ wall (vs CHUNK) | mean est GFLOPs | Δ GFLOPs | n |
|--------|-----------------|-----------------|--------------|-------------------|-----------------|----------|---|
| H-EARLY | -16.7880 | — | 78 | — | 42.938 | — | 3 |
| H-CHUNK | -16.7878 | +0.0002 | 37 | — | 48.921 | — | 3 |
| H-CHB-B128 | -16.7878 | +0.0002 | 35 | — | 44.902 | — | 3 |
| H-CHB-B256 | -16.7878 | +0.0002 | 34 | — | 44.206 | — | 3 |
| H-CHB-B64 | -16.7878 | +0.0002 | 35 | — | 46.242 | — | 3 |
| H-CHB | -16.7878 | +0.0002 | 34 | -3 | 45.224 | -3.697 | 3 |

**Decision: PROMOTE (chunk_size sweep beats H-CHUNK tip)**

Systems util deepen on CHUNK; tip EARLY / CHUNK B=32 unchanged unless PROMOTE replaces util knob.

Commands: `npm run nano:chb` → `npm run nano:chb:report`.
