# H-GALLF smoke — CUDA graph all budgets under GRAPHF

Same B2 + POOL + LAY; H-GRAPHF keeps dual-budget (CPOOLB when KV on). H-GALLF forces full-depth CUDAGraph on every budget (never KV). Kill if |Δlp| > ε vs H-GRAPHF or no wall win.
Prompt pack: smoke+fit elongated (`n_prompts=4`); budgets=`[16, 64]` target_tokens=`128`; mode `CUDA graph all budgets (never KV) vs GRAPHF dual-budget`.

| family | mean teacher_lp | Δ lp | mean tok/s | Δ tok/s | mean wall_ms/prompt | Δ wall | mean est GFLOPs | Δ GFLOPs | n |
|--------|-----------------|------|------------|---------|---------------------|--------|-----------------|----------|---|
| H-GRAPHF | -10.4872 | — | 2169.9 | — | 18 | — | 43.431 | — | 3 |
| H-GALLF | -10.4872 | +0.0000 | 1274.3 | -895.5 | 33 | +15 | 42.987 | -0.445 | 3 |

**Decision: KILL (no wall win vs H-GRAPHF)**

Systems util under GRAPHF — tip POOL / util GRAPHF unchanged.

Commands: `npm run nano:gallf` → `npm run nano:gallf:report`.
