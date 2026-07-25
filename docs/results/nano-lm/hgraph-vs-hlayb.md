# H-GRAPH smoke — CUDA graph under LAYB decode

Same dual-budget LAYB path on B2; non-KV arm uses full-depth per-T CUDAGraph replay (capture untimed). KV arm stays CHBAT. Kill if |Δlp| > ε vs H-LAYB or no wall win.
Prompt pack: smoke+fit elongated (`n_prompts=4`); budgets=`[16, 64]` target_tokens=`128`; mode `CUDA graph full-depth LAY arm under LAYB; capture untimed`.

| family | mean teacher_lp | Δ lp | mean tok/s | Δ tok/s | mean wall_ms/prompt | Δ wall | mean est GFLOPs | Δ GFLOPs | n |
|--------|-----------------|------|------------|---------|---------------------|--------|-----------------|----------|---|
| H-LAYB | -12.5914 | — | 1679.0 | — | 11 | — | 6.111 | — | 3 |
| H-GRAPH | -12.5914 | +0.0000 | 2747.3 | +1068.3 | 2 | -8 | 6.111 | +0.000 | 3 |

**Decision: PROMOTE (CUDA graph under LAYB decode)**

Systems util under LAYB — tip EARLY / util LAYB unchanged.

Commands: `npm run nano:graph` → `npm run nano:graph:report`.
