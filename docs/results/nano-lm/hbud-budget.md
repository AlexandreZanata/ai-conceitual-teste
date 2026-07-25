# H-BUD smoke — hard wall/GFLOPs budget vs tip

Pareto hard gate: recipe must stay within tip wall **and** tip·(1+δ) GFLOPs (δ=`0.05`), keep quality floor, and still win wall↓ or tok/s↑. Train: ms/step ≤ tip with strict ms/step↓. PACK gated on **SERVE** (min-wall); SROUTE is GFLOPs-inflated by design.
Mode: `hard wall+GFLOPs (ms/step) budget vs tip`; n_prompts=`4`; budgets=`[16, 64]`; target=`128`.

| recipe | util | tip | verdict |
|--------|------|-----|---------|
| H-PACK | H-SERVE | H-EARLY | SURVIVE (wall+GFLOPs budgets + win) |
| H-QPACK | H-FLAYB | H-POOL | SURVIVE (wall+GFLOPs budgets + win) |
| H-TPACK | H-TPACK | H-STAG | SURVIVE (ms/step budget + win) |

**Decision: PROMOTE (budget survivors: H-PACK+H-QPACK+H-TPACK)**

## H-PACK (SERVE vs EARLY)

| family | mean teacher_lp | Δ lp | mean tok/s | Δ tok/s | mean wall_ms | Δ wall | mean est GFLOPs | Δ GFLOPs | n |
|--------|-----------------|------|------------|---------|--------------|--------|-----------------|----------|---|
| H-EARLY | -12.5933 | — | 612.6 | — | 16 | — | 6.111 | — | 3 |
| H-SERVE | -12.5914 | +0.0019 | 1255.5 | +642.8 | 6 | -11 | 6.111 | +0.000 | 3 |

## H-QPACK (FLAYB vs POOL)

| family | mean teacher_lp | Δ lp | mean tok/s | Δ tok/s | mean wall_ms | Δ wall | mean est GFLOPs | Δ GFLOPs | n |
|--------|-----------------|------|------------|---------|--------------|--------|-----------------|----------|---|
| H-POOL | -10.4879 | — | 690.3 | — | 57 | — | 42.987 | — | 3 |
| H-FLAYB | -10.4872 | +0.0007 | 2647.9 | +1957.6 | 14 | -43 | 43.431 | +0.445 | 3 |

## H-TPACK (vs STAG ms/step)

| family | mean teacher_lp | Δ lp | mean ms/step | Δ ms/step | n |
|--------|-----------------|------|--------------|-----------|---|
| H-STAG | -17.0327 | — | 8.9 | — | 3 |
| H-TPACK | -16.6988 | +0.3340 | 5.6 | -3.4 | 3 |

Tips unchanged. Wave U budget hygiene.

Commands: `npm run nano:bud` → `npm run nano:bud:report`.
