# Formal H-BUD — hard wall/GFLOPs budget vs tip

Source: `results/nano-lm/formal-hbud/formal.json`
Wall clock: 221.9s

Pareto hard gate: recipe must stay within tip wall **and** tip·(1+δ) GFLOPs (δ=`0.05`), keep quality floor, and still win wall↓ or tok/s↑. Train: ms/step ≤ tip with strict ms/step↓. PACK gated on **SERVE** (min-wall); SROUTE is GFLOPs-inflated by design.
Mode: `hard wall+GFLOPs (ms/step) budget vs tip`; n_prompts=`10`; budgets=`[16, 64]`; target=`128`.

| recipe | util | tip | verdict |
|--------|------|-----|---------|
| H-PACK | H-SERVE | H-EARLY | SURVIVE (wall+GFLOPs budgets + win) |
| H-QPACK | H-FLAYB | H-POOL | SURVIVE (wall+GFLOPs budgets + win) |
| H-TPACK | H-TPACK | H-STAG | SURVIVE (ms/step budget + win) |

**Decision: PROMOTE (budget survivors: H-PACK+H-QPACK+H-TPACK)**

## H-PACK (SERVE vs EARLY)

| family | mean teacher_lp | Δ lp | mean tok/s | Δ tok/s | mean wall_ms | Δ wall | mean est GFLOPs | Δ GFLOPs | n |
|--------|-----------------|------|------------|---------|--------------|--------|-----------------|----------|---|
| H-EARLY | -13.9921 | — | 653.4 | — | 14 | — | 7.393 | — | 3 |
| H-SERVE | -13.9918 | +0.0003 | 2623.6 | +1970.2 | 3 | -11 | 7.393 | +0.000 | 3 |

## H-QPACK (FLAYB vs POOL)

| family | mean teacher_lp | Δ lp | mean tok/s | Δ tok/s | mean wall_ms | Δ wall | mean est GFLOPs | Δ GFLOPs | n |
|--------|-----------------|------|------------|---------|--------------|--------|-----------------|----------|---|
| H-POOL | -12.3589 | — | 703.9 | — | 57 | — | 43.000 | — | 3 |
| H-FLAYB | -12.3583 | +0.0006 | 5346.5 | +4642.6 | 7 | -50 | 43.593 | +0.593 | 3 |

## H-TPACK (vs STAG ms/step)

| family | mean teacher_lp | Δ lp | mean ms/step | Δ ms/step | n |
|--------|-----------------|------|--------------|-----------|---|
| H-STAG | -13.2775 | — | 18.3 | — | 3 |
| H-TPACK | -12.4946 | +0.7828 | 14.3 | -4.0 | 3 |

Tips unchanged. Wave U budget hygiene.

Commands: `npm run nano:formal:hbud` → `npm run nano:formal:hbud:report`.
