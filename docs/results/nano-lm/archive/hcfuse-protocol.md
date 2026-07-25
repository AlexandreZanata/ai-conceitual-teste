# H-CFUSE protocol — CHUNK ⊕ FUSE (FLASH⊕KVSEL)

Stack **decode utils** H-CHUNK (chunked KV prefill) and H-FUSE (FLASH SDPA ⊕ KVSEL gated KV) on frozen EARLY tip genes + frozen `kv_threshold` / `chunk_size`.
Long prompts + dual-budget mean (same budgets as H-KVSEL).
This is a **protocol note**, not a compose tip H-ID.
PROTOCOL iff lp ≥ EARLY−ε and wall < min(CHUNK, FUSE); else KILL.
Note: `protocol stack; not a tip H-ID`. Budgets: `[16, 64]`. chunk_size=`32` target_tokens=`128`.

| family | mean teacher_lp | Δ lp vs EARLY | mean wall_ms | Δ vs min(C,F) | mean est GFLOPs | n |
|--------|-----------------|---------------|--------------|---------------|-----------------|---|
| H-EARLY | -16.4808 | — | 59 | — | 57.673 | 3 |
| H-CHUNK | -16.4804 | +0.0004 | 46 | — | 63.799 | 3 |
| H-FUSE | -16.4804 | +0.0004 | 43 | — | 8.299 | 3 |
| H-CFUSE | -16.4804 | +0.0004 | 46 | +2 | 60.950 | 3 |

**Decision: KILL (wall ≥ min(CHUNK,FUSE); stack adds no value)**

Tips stay separate: decode **H-EARLY** (+ optional CHUNK / FUSE). Do not invent H-CFUSE tip.

Commands: `npm run nano:cfuse` → `npm run nano:cfuse:report`.
