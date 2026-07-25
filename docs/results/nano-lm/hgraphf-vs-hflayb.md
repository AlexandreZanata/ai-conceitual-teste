# H-GRAPHF smoke — CUDA graph under FLAYB decode

Same dual-budget FLAYB path on B2; non-KV arm uses full-depth per-T CUDAGraph replay (capture untimed). KV arm stays CPOOLB. Kill if |Δlp| > ε vs H-FLAYB or no wall win.
Prompt pack: smoke+fit elongated (`n_prompts=4`); budgets=`[16, 64]` target_tokens=`128`; mode `CUDA graph full-depth BoN+LAY arm under FLAYB; capture untimed`.

| family | mean teacher_lp | Δ lp | mean tok/s | Δ tok/s | mean wall_ms/prompt | Δ wall | mean est GFLOPs | Δ GFLOPs | n |
|--------|-----------------|------|------------|---------|---------------------|--------|-----------------|----------|---|
| H-FLAYB | -10.4872 | — | 1891.4 | — | 29 | — | 43.431 | — | 3 |
| H-GRAPHF | -10.4872 | +0.0000 | 3147.4 | +1256.0 | 13 | -17 | 43.431 | +0.000 | 3 |

**Decision: PROMOTE (CUDA graph under FLAYB decode)**

Systems util under FLAYB — tip POOL / util FLAYB unchanged.

Commands: `npm run nano:graphf` → `npm run nano:graphf:report`.
