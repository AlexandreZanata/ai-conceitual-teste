# Formal H-GRAPHF vs H-FLAYB (CUDA graph under FLAYB decode)

Source: `results/nano-lm/formal-hgraphf/formal.json`
Wall clock: 19.4s

Shared formal B2 + POOL + LAY + KVSEL. Fit≠eval.
Dual-budget FLAYB with CUDA-graph full-depth non-KV arm vs tip FLAYB.
Mode: `CUDA graph full-depth BoN+LAY arm under FLAYB; capture untimed; long eval`. Kill if |Δlp| > ε or no wall win.
n_prompts=8 chunk_size=`256` budgets=`[16, 64]` target_tokens=`128`.

| family | mean teacher_lp | Δ lp | mean tok/s | Δ tok/s | mean wall_ms/prompt | Δ wall | n |
|--------|-----------------|------|------------|---------|---------------------|--------|---|
| H-FLAYB | -12.4433 | — | 3823.3 | — | 12 | — | 3 |
| H-GRAPHF | -12.4433 | +0.0000 | 4957.9 | +1134.5 | 8 | -5 | 3 |

**Decision:** PROMOTE (CUDA graph under FLAYB decode)

Systems util under FLAYB — does not replace H-POOL / H-FLAYB.

Commands: `npm run nano:formal:hgraphf` → `npm run nano:formal:hgraphf:report`.
