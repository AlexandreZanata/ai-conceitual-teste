# Formal H-CHB vs H-CHUNK (chunk_size sweep winner)

Source: `results/nano-lm/formal-hchb/formal.json`
Wall clock: 14.7s

Shared formal B2 + formal EARLY. Fit≠eval (`eval_prompts`).
Frozen smoke `chunk_size` vs tip CHUNK `B=32`. Long prompts.
Mode: `frozen smoke chunk_size vs tip`. Kill if lp < EARLY−ε or wall ≥ tip.
n_prompts=8 target_tokens=`128`.

| family | mean teacher_lp | Δ lp (vs EARLY) | mean wall_ms | Δ wall (vs CHUNK) | n |
|--------|-----------------|-----------------|--------------|-------------------|---|
| H-EARLY | -12.0007 | — | 83 | — | 3 |
| H-CHUNK | -12.0006 | +0.0001 | 57 | — | 3 |
| H-CHB | -12.0006 | +0.0001 | 55 | -1 | 3 |

**Decision:** PROMOTE (chunk_size sweep beats H-CHUNK tip)

Systems util deepen on CHUNK; tip EARLY unchanged.

Commands: `npm run nano:formal:hchb` → `npm run nano:formal:hchb:report`.
