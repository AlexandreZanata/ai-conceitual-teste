# Formal H-GALL vs H-GRAPH (CUDA graph all budgets)

Source: `results/nano-lm/formal-hgall/formal.json`
Wall clock: 10.9s

Shared formal B2 + EARLY + LAY + KVSEL. Fit≠eval.
H-GRAPH dual-budget vs H-GALL graph-all (never KV).
Mode: `CUDA graph all budgets (never KV) vs GRAPH; long eval`. Kill if |Δlp| > ε or no wall win.
n_prompts=8 chunk_size=`256` budgets=`[16, 64]` target_tokens=`128`.

| family | mean teacher_lp | Δ lp | mean tok/s | Δ tok/s | mean wall_ms/prompt | Δ wall | n |
|--------|-----------------|------|------------|---------|---------------------|--------|---|
| H-GRAPH | -13.9851 | — | 3023.5 | — | 6 | — | 3 |
| H-GALL | -13.9851 | +0.0000 | 2451.2 | -572.3 | 3 | -3 | 3 |

**Decision:** PROMOTE (CUDA graph all budgets under GRAPH)

Systems util under GRAPH — does not replace H-EARLY / H-GRAPH.

Commands: `npm run nano:formal:hgall` → `npm run nano:formal:hgall:report`.
