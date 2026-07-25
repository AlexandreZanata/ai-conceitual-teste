# H-PACK smoke — SERVE=min-wall + SROUTE=Pareto vs H-EARLY

Card hygiene: freeze both serving packs against tip EARLY on the same prompts/budgets. SERVE requires |Δlp|≤ε; SROUTE requires lp≥EARLY−ε; both need wall↓ or tok/s↑.
Prompt pack: `n_prompts=4`; budgets=`[16, 64]` chunk=`256` target_tokens=`128`; mode `SERVE=min-wall + SROUTE=Pareto vs EARLY`.

| family | mean teacher_lp | Δ lp | mean tok/s | Δ tok/s | mean wall_ms | Δ wall | mean est GFLOPs | n |
|--------|-----------------|------|------------|---------|--------------|--------|-----------------|---|
| H-EARLY | -12.5933 | — | 602.7 | — | 16 | — | 6.111 | 3 |
| H-SERVE | -12.5914 | +0.0019 | 1274.1 | +671.4 | 6 | -10 | 6.111 | 3 |
| H-SROUTE | -10.8930 | +1.7003 | 2339.7 | +1736.9 | 12 | -4 | 38.918 | 3 |

**Decision: PROMOTE (SERVE=min-wall + SROUTE=Pareto packs vs EARLY)**

Tip H-EARLY unchanged. Packs: SERVE=min-wall, SROUTE=Pareto.

Commands: `npm run nano:pack` → `npm run nano:pack:report`.
