# H-FCPOOLB smoke — FUSE (FLASH⊕KVSEL) under CPOOLB batch

Dual-budget mean: FLASH SDPA + KVSEL gate on CPOOLB path (B=`256`). Chunked CPOOLB when `max_new > kv_threshold`; else flat POOLB.
Control = always-on H-CPOOLB. Kill if |Δlp| > ε or no tok/s/wall win.
Prompt pack: smoke+fit elongated (`n_prompts=4`); budgets=`[16, 64]` target_tokens=`128`; mode `dual-budget FUSE under CPOOLB; n=1 near-greedy; long prompts`.
Selected `kv_threshold` per seed: `[48, 48, 48]`.

| family | mean teacher_lp | Δ lp | mean tok/s | Δ tok/s | mean wall_ms/prompt | Δ wall | mean est GFLOPs | Δ GFLOPs | n |
|--------|-----------------|------|------------|---------|---------------------|--------|-----------------|----------|---|
| H-CPOOLB | -10.4872 | — | 2672.9 | — | 19 | — | 43.876 | — | 3 |
| H-FCPOOLB | -10.4872 | +0.0000 | 2686.3 | +13.4 | 14 | -6 | 43.431 | -0.445 | 3 |

**Decision: PROMOTE (FUSE under CPOOLB batch)**

Throughput util on CPOOLB axis — tip POOL / util CPOOLB unchanged as tips.

Commands: `npm run nano:fcpoolb` → `npm run nano:fcpoolb:report`.
