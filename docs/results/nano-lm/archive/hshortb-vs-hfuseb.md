# H-SHORTB smoke — SHORT under FUSEB dual-budget batch

Dual-budget mean: FUSEB path with batched SHORT on the non-KV arm (CHBAT B=`256` when `max_new > kv_threshold`).
Frozen SHORT tip `draft_max` / `stop_conf`. Kill if |Δlp| > ε vs H-FUSEB or no tok/s/wall win.
Prompt pack: smoke+fit elongated (`n_prompts=4`); budgets=`[16, 64]` target_tokens=`128`; mode `dual-budget SHORT under FUSEB; n=1 near-greedy; long prompts`.
Selected SHORT knobs per seed: `[{'draft_max': 8, 'stop_conf': 0.7}, {'draft_max': 4, 'stop_conf': 0.85}, {'draft_max': 4, 'stop_conf': 0.55}]`.

| family | mean teacher_lp | Δ lp | mean tok/s | Δ tok/s | mean wall_ms/prompt | Δ wall | mean est GFLOPs | Δ GFLOPs | n |
|--------|-----------------|------|------------|---------|---------------------|--------|-----------------|----------|---|
| H-FUSEB | -12.5914 | — | 1610.4 | — | 11 | — | 6.111 | — | 3 |
| H-SHORTB | -12.7274 | -0.1359 | 2718.2 | +1107.9 | 2 | -9 | 5.489 | -0.622 | 3 |

**Decision: KILL (lp change vs H-FUSEB)**

Throughput util on FUSEB axis — tip EARLY / util FUSEB / SHORT unchanged.

Commands: `npm run nano:shortb` → `npm run nano:shortb:report`.
