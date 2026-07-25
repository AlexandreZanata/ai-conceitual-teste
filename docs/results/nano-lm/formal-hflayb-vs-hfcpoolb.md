# Formal H-FLAYB vs H-FCPOOLB (LAY under FCPOOLB batch)

Source: `results/nano-lm/formal-hflayb/formal.json`
Wall clock: 18.0s

Shared formal B2 + POOL + LAY + KVSEL. Fit≠eval.
Dual-budget FCPOOLB with batched BoN+LAY on non-KV arm vs tip FCPOOLB.
Mode: `dual-budget LAY under FCPOOLB; n=1 near-greedy; long eval`. Kill if |Δlp| > ε or no tok/s/wall win.
n_prompts=8 chunk_size=`256` budgets=`[16, 64]` target_tokens=`128`.
Selected LAY knobs per seed: `[{'max_skip': 1, 'lay_conf': 0.9063302391634451}, {'max_skip': 0, 'lay_conf': 0.8839393297930102}, {'max_skip': 0, 'lay_conf': 0.6483670871310137}]`.

| family | mean teacher_lp | Δ lp | mean tok/s | Δ tok/s | mean wall_ms/prompt | Δ wall | n |
|--------|-----------------|------|------------|---------|---------------------|--------|---|
| H-FCPOOLB | -12.4433 | — | 3877.0 | — | 12 | — | 3 |
| H-FLAYB | -12.4433 | +0.0000 | 4957.0 | +1080.1 | 8 | -4 | 3 |

**Decision:** PROMOTE (LAY under FCPOOLB batch)

Throughput util on FCPOOLB axis — does not replace H-POOL / H-FCPOOLB / H-LAY.

Commands: `npm run nano:formal:hflayb` → `npm run nano:formal:hflayb:report`.
