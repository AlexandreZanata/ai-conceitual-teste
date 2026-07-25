# H-FLAYB smoke — LAY under FCPOOLB dual-budget batch

Dual-budget mean: FCPOOLB path with batched BoN+LAY on the non-KV arm (CPOOLB B=`256` when `max_new > kv_threshold`).
Frozen LAY tip `max_skip` / `lay_conf`. Kill if |Δlp| > ε vs H-FCPOOLB or no tok/s/wall win.
Prompt pack: smoke+fit elongated (`n_prompts=4`); budgets=`[16, 64]` target_tokens=`128`; mode `dual-budget LAY under FCPOOLB; n=1 near-greedy; long prompts`.
Selected LAY knobs per seed: `[{'max_skip': 1, 'lay_conf': 0.853181761176121}, {'max_skip': 0, 'lay_conf': 0.7776815499288849}, {'max_skip': 0, 'lay_conf': 0.55247220198751}]`.

| family | mean teacher_lp | Δ lp | mean tok/s | Δ tok/s | mean wall_ms/prompt | Δ wall | mean est GFLOPs | Δ GFLOPs | n |
|--------|-----------------|------|------------|---------|---------------------|--------|-----------------|----------|---|
| H-FCPOOLB | -10.4872 | — | 2190.1 | — | 22 | — | 43.431 | — | 3 |
| H-FLAYB | -10.4872 | +0.0000 | 2626.4 | +436.3 | 14 | -8 | 43.431 | +0.000 | 3 |

**Decision: PROMOTE (LAY under FCPOOLB batch)**

Throughput util on FCPOOLB axis — tip POOL / util FCPOOLB / LAY unchanged.

Commands: `npm run nano:flayb` → `npm run nano:flayb:report`.
