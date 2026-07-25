# H-LAYB smoke — LAY under FUSEB dual-budget batch

Dual-budget mean: FUSEB path with batched LAY on the non-KV arm (CHBAT B=`256` when `max_new > kv_threshold`).
Frozen LAY tip `max_skip` / `lay_conf`. Kill if |Δlp| > ε vs H-FUSEB or no tok/s/wall win.
Prompt pack: smoke+fit elongated (`n_prompts=4`); budgets=`[16, 64]` target_tokens=`128`; mode `dual-budget LAY under FUSEB; n=1 near-greedy; long prompts`.
Selected LAY knobs per seed: `[{'max_skip': 1, 'lay_conf': 0.853181761176121}, {'max_skip': 0, 'lay_conf': 0.7776815499288849}, {'max_skip': 0, 'lay_conf': 0.55247220198751}]`.

| family | mean teacher_lp | Δ lp | mean tok/s | Δ tok/s | mean wall_ms/prompt | Δ wall | mean est GFLOPs | Δ GFLOPs | n |
|--------|-----------------|------|------------|---------|---------------------|--------|-----------------|----------|---|
| H-FUSEB | -12.5914 | — | 1796.1 | — | 10 | — | 6.111 | — | 3 |
| H-LAYB | -12.5914 | +0.0000 | 2360.3 | +564.1 | 3 | -7 | 6.111 | +0.000 | 3 |

**Decision: PROMOTE (LAY under FUSEB batch)**

Throughput util on FUSEB axis — tip EARLY / util FUSEB / LAY unchanged.

Commands: `npm run nano:layb` → `npm run nano:layb:report`.
