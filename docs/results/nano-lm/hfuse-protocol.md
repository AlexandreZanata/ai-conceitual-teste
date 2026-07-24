# H-FUSE protocol — FLASH ⊕ KVSEL

Stack **decode utils** H-FLASH (SDPA) and H-KVSEL (gated KV) on frozen EARLY tip genes + frozen `kv_threshold` from prior KVSEL smoke.
Dual-budget mean over the same budgets as H-KVSEL.
This is a **protocol note**, not a compose tip H-ID.
PROTOCOL iff lp ≥ EARLY−ε and wall < min(FLASH, KVSEL); else KILL.
Note: `protocol stack; not a tip H-ID`. Budgets: `[16, 64]`.

| family | mean teacher_lp | Δ lp vs EARLY | mean wall_ms | Δ vs min(F,K) | mean est GFLOPs | n |
|--------|-----------------|---------------|--------------|---------------|-----------------|---|
| H-EARLY | -16.2866 | — | 55 | — | 15.164 | 3 |
| H-FLASH | -16.2870 | -0.0003 | 43 | — | 15.164 | 3 |
| H-KVSEL | -16.2866 | +0.0000 | 50 | — | 1.524 | 3 |
| H-FUSE | -16.2870 | -0.0003 | 41 | -1 | 1.524 | 3 |

**Decision: PROTOCOL (FLASH ⊕ KVSEL; not a tip H-ID)**

Tips stay separate: decode **H-EARLY** (+ optional FLASH or KVSEL). Do not invent H-FUSE tip.

Commands: `npm run nano:fuse` → `npm run nano:fuse:report`.
