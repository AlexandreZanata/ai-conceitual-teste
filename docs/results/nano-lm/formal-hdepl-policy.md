# Formal H-DEPL — deploy policy gated on BUD survivors

Source: `results/nano-lm/formal-hdepl/formal.json`
Wall clock: 238.2s

Runnable deploy policy (Wave V): **speed** → H-PACK (not ood_long); **quality** → H-QPACK only if in-dist; **train** → H-TPACK. Kill if any chosen recipe fails H-BUD SURVIVE (policy contradicts BUD).
Mode: `DEPL: BUD survivors → deploy policy (speed/quality/train)`; n_prompts=`10`; budgets=`[16, 64]`; target=`128`; cpu_threads=`12`; δ=`0.05`.

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
| H-EARLY | -13.9921 | — | 662.3 | — | 14 | — | 7.393 | 3 |
| H-SERVE | -13.9918 | +0.0003 | 2800.9 | +2138.5 | 3 | -11 | 7.393 | 3 |

## H-QPACK (FLAYB vs POOL)

| family | mean teacher_lp | Δ lp | mean tok/s | Δ tok/s | mean wall_ms | Δ wall | mean est GFLOPs | n |
|--------|-----------------|------|------------|---------|--------------|--------|-----------------|---|
| H-POOL | -12.3589 | — | 682.9 | — | 57 | — | 43.000 | 3 |
| H-FLAYB | -12.3583 | +0.0006 | 5518.9 | +4836.0 | 7 | -50 | 43.593 | 3 |

## H-TPACK (vs STAG ms/step)

| family | mean teacher_lp | Δ lp | mean ms/step | Δ ms/step | n |
|--------|-----------------|------|--------------|-----------|---|
| H-STAG | -13.2775 | — | 18.1 | — | 3 |
| H-TPACK | -12.4946 | +0.7828 | 14.2 | -3.8 | 3 |

Tips unchanged. Wave V deploy policy.

Commands: `npm run nano:formal:hdepl` → `npm run nano:formal:hdepl:report`.
