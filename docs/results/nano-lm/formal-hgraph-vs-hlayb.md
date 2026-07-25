# Formal H-GRAPH vs H-LAYB (CUDA graph under LAYB decode)

Source: `results/nano-lm/formal-hgraph/formal.json`
Wall clock: 10.5s

Shared formal B2 + EARLY + LAY + KVSEL. Fit≠eval.
Dual-budget LAYB with CUDA-graph full-depth non-KV arm vs tip LAYB.
Mode: `CUDA graph full-depth LAY arm under LAYB; capture untimed; long eval`. Kill if |Δlp| > ε or no wall win.
n_prompts=8 chunk_size=`256` budgets=`[16, 64]` target_tokens=`128`.

| family | mean teacher_lp | Δ lp | mean tok/s | Δ tok/s | mean wall_ms/prompt | Δ wall | n |
|--------|-----------------|------|------------|---------|---------------------|--------|---|
| H-LAYB | -13.9851 | — | 3233.5 | — | 6 | — | 3 |
| H-GRAPH | -13.9851 | +0.0000 | 4321.4 | +1087.9 | 2 | -4 | 3 |

**Decision:** PROMOTE (CUDA graph under LAYB decode)

Systems util under LAYB — does not replace H-EARLY / H-LAYB.

Commands: `npm run nano:formal:hgraph` → `npm run nano:formal:hgraph:report`.
