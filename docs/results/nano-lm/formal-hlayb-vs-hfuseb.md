# Formal H-LAYB vs H-FUSEB (LAY under FUSEB batch)

Source: `results/nano-lm/formal-hlayb/formal.json`
Wall clock: 9.4s

Shared formal B2 + EARLY + LAY + KVSEL. Fit≠eval.
Dual-budget FUSEB with batched LAY on non-KV arm vs tip FUSEB.
Mode: `dual-budget LAY under FUSEB; n=1 near-greedy; long eval`. Kill if |Δlp| > ε or no tok/s/wall win.
n_prompts=8 chunk_size=`256` budgets=`[16, 64]` target_tokens=`128`.
Selected LAY knobs per seed: `[{'max_skip': 1, 'lay_conf': 0.9063302391634451}, {'max_skip': 0, 'lay_conf': 0.8839393297930102}, {'max_skip': 0, 'lay_conf': 0.6483670871310137}]`.

| family | mean teacher_lp | Δ lp | mean tok/s | Δ tok/s | mean wall_ms/prompt | Δ wall | n |
|--------|-----------------|------|------------|---------|---------------------|--------|---|
| H-FUSEB | -13.9851 | — | 3209.0 | — | 6 | — | 3 |
| H-LAYB | -13.9851 | +0.0000 | 4210.8 | +1001.8 | 2 | -4 | 3 |

**Decision:** PROMOTE (LAY under FUSEB batch)

Throughput util on FUSEB axis — does not replace H-EARLY / H-FUSEB / H-LAY.

Commands: `npm run nano:formal:hlayb` → `npm run nano:formal:hlayb:report`.
