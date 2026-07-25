# Formal H-FCPOOLB vs H-CPOOLB (FUSE under CPOOLB batch)

Source: `results/nano-lm/formal-hfcpoolb/formal.json`
Wall clock: 17.5s

Shared formal B2 + POOL + formal KVSEL threshold. Fit≠eval.
Dual-budget FLASH⊕KVSEL gate on CPOOLB path vs always-on CPOOLB.
Mode: `dual-budget FUSE under CPOOLB; n=1 near-greedy; long eval`. Kill if |Δlp| > ε or no tok/s/wall win.
n_prompts=8 chunk_size=`256` budgets=`[16, 64]` target_tokens=`128`.
Selected `kv_threshold` per seed: `[0, 32, 32]`.

| family | mean teacher_lp | Δ lp | mean tok/s | Δ tok/s | mean wall_ms/prompt | Δ wall | n |
|--------|-----------------|------|------------|---------|---------------------|--------|---|
| H-CPOOLB | -12.4433 | — | 4626.6 | — | 11 | — | 3 |
| H-FCPOOLB | -12.4433 | +0.0000 | 4913.1 | +286.5 | 8 | -4 | 3 |

**Decision:** PROMOTE (FUSE under CPOOLB batch)

Throughput util on CPOOLB axis — does not replace H-POOL / H-CPOOLB tips.

Commands: `npm run nano:formal:hfcpoolb` → `npm run nano:formal:hfcpoolb:report`.
