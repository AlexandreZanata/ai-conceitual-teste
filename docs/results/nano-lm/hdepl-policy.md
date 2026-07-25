# H-DEPL smoke — deploy policy gated on BUD survivors

Runnable deploy policy (Wave V): **speed** → H-PACK (not ood_long); **quality** → H-QPACK only if in-dist; **train** → H-TPACK. Kill if any chosen recipe fails H-BUD SURVIVE (policy contradicts BUD).
Mode: `DEPL: BUD survivors → deploy policy (speed/quality/train)`; n_prompts=`4`; budgets=`[16, 64]`; target=`128`; cpu_threads=`12`; δ=`0.05`.

## BUD survivors

| recipe | util | tip | verdict |
|--------|------|-----|---------|
| H-PACK | H-SERVE | H-EARLY | SURVIVE (wall+GFLOPs budgets + win) |
| H-QPACK | H-FLAYB | H-POOL | SURVIVE (wall+GFLOPs budgets + win) |
| H-TPACK | H-TPACK | H-STAG | SURVIVE (ms/step budget + win) |

## Deploy routes

| scenario | goal | in_dist | ood_long | choice |
|----------|------|---------|----------|--------|
| speed_in_dist | speed | True | False | H-PACK |
| speed_ood_long | speed | False | True | REJECT (PACK forbidden on ood_long) |
| quality_in_dist | quality | True | False | H-QPACK |
| quality_ood | quality | False | False | REJECT (QPACK requires in-dist) |
| train_steps | train | True | False | H-TPACK |

**Decision: PROMOTE (deploy policy consistent: speed_in_dist→H-PACK;speed_ood_long→REJECT (PACK forbidden on ood_long);quality_in_dist→H-QPACK;quality_ood→REJECT (QPACK requires in-dist);train_steps→H-TPACK)**

## H-PACK (SERVE vs EARLY)

| family | mean teacher_lp | Δ lp | mean tok/s | Δ tok/s | mean wall_ms | Δ wall | mean est GFLOPs | n |
|--------|-----------------|------|------------|---------|--------------|--------|-----------------|---|
| H-EARLY | -12.5933 | — | 637.9 | — | 16 | — | 6.111 | 3 |
| H-SERVE | -12.5914 | +0.0019 | 1242.8 | +604.9 | 6 | -10 | 6.111 | 3 |

## H-QPACK (FLAYB vs POOL)

| family | mean teacher_lp | Δ lp | mean tok/s | Δ tok/s | mean wall_ms | Δ wall | mean est GFLOPs | n |
|--------|-----------------|------|------------|---------|--------------|--------|-----------------|---|
| H-POOL | -10.4879 | — | 727.8 | — | 54 | — | 42.987 | 3 |
| H-FLAYB | -10.4872 | +0.0007 | 2696.7 | +1968.9 | 14 | -41 | 43.431 | 3 |

## H-TPACK (vs STAG ms/step)

| family | mean teacher_lp | Δ lp | mean ms/step | Δ ms/step | n |
|--------|-----------------|------|--------------|-----------|---|
| H-STAG | -17.0327 | — | 9.1 | — | 3 |
| H-TPACK | -16.6988 | +0.3340 | 5.6 | -3.5 | 3 |

Tips unchanged. Wave V deploy policy.

Commands: `npm run nano:depl` → `npm run nano:depl:report`.
