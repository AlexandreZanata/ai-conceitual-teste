# H-GALL smoke — CUDA graph all budgets under GRAPH

Same B2 + EARLY + LAY; H-GRAPH keeps dual-budget (CHBAT when KV on). H-GALL forces full-depth CUDAGraph on every budget (never KV). Kill if |Δlp| > ε vs H-GRAPH or no wall win.
Prompt pack: smoke+fit elongated (`n_prompts=4`); budgets=`[16, 64]` target_tokens=`128`; mode `CUDA graph all budgets (never KV) vs GRAPH dual-budget`.

| family | mean teacher_lp | Δ lp | mean tok/s | Δ tok/s | mean wall_ms/prompt | Δ wall | mean est GFLOPs | Δ GFLOPs | n |
|--------|-----------------|------|------------|---------|---------------------|--------|-----------------|----------|---|
| H-GRAPH | -12.5914 | — | 1563.7 | — | 7 | — | 6.111 | — | 3 |
| H-GALL | -12.5914 | +0.0000 | 1286.7 | -277.0 | 5 | -1 | 6.111 | +0.000 | 3 |

**Decision: PROMOTE (CUDA graph all budgets under GRAPH)**

Systems util under GRAPH — tip EARLY / util GRAPH unchanged.

Commands: `npm run nano:gall` → `npm run nano:gall:report`.
