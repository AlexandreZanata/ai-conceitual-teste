# Formal H-SROUTE vs H-SERVE (ROUTE as serving default?)

Source: `results/nano-lm/formal-hsroute/formal.json`
Wall clock: 19.4s

Fit≠eval. ROUTE vs frozen SERVE on (lp, wall). Kill if SERVE dominates; else PROMOTE.
n_prompts=10 chunk_size=`256` budgets=`[16, 64]` target_tokens=`128`.

| family | mean teacher_lp | Δ lp | mean tok/s | Δ tok/s | mean wall_ms/prompt | Δ wall | mean est GFLOPs | n |
|--------|-----------------|------|------------|---------|---------------------|--------|-----------------|---|
| H-SERVE | -13.9918 | — | 2760.5 | — | 3 | — | 7.393 | 3 |
| H-SROUTE | -12.3959 | +1.5960 | 5303.9 | +2543.4 | 6 | +3 | 41.016 | 3 |

**Decision:** PROMOTE (ROUTE not dominated by SERVE)

Full-stack serving claim (Wave S). Tips unchanged.

Commands: `npm run nano:formal:hsroute` → `npm run nano:formal:hsroute:report`.
