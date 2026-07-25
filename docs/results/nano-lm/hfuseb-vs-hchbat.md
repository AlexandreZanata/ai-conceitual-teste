# H-FUSEB smoke — FUSE (FLASH⊕KVSEL) under CHBAT batch

Dual-budget mean: FLASH SDPA + KVSEL gate on CHBAT path (B=`256`). Chunked CBAT when `max_new > kv_threshold`; else flat BAT.
Control = always-on H-CHBAT. Kill if |Δlp| > ε or no tok/s/wall win.
Prompt pack: smoke+fit elongated (`n_prompts=4`); budgets=`[16, 64]` target_tokens=`128`; mode `dual-budget FUSE under CHBAT; n=1 near-greedy; long prompts`.
Selected `kv_threshold` per seed: `[48, 48, 48]`.

| family | mean teacher_lp | Δ lp | mean tok/s | Δ tok/s | mean wall_ms/prompt | Δ wall | mean est GFLOPs | Δ GFLOPs | n |
|--------|-----------------|------|------------|---------|---------------------|--------|-----------------|----------|---|
| H-CHBAT | -12.5914 | — | 2111.4 | — | 11 | — | 6.111 | — | 3 |
| H-FUSEB | -12.5914 | +0.0000 | 2288.4 | +177.0 | 3 | -8 | 6.111 | +0.000 | 3 |

**Decision: PROMOTE (FUSE under CHBAT batch)**

Throughput util on CHBAT axis — tip EARLY / util CHBAT unchanged as tips.

Commands: `npm run nano:fuseb` → `npm run nano:fuseb:report`.
