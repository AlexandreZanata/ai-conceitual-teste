# H-SROUTE smoke — ROUTE vs frozen H-SERVE

Full-stack head-to-head: length-budget ROUTE vs frozen SERVE recipe (best of GALL-speed / GRAPHF-quality). Kill if SERVE dominates on (lp, wall).
Prompt pack: `n_prompts=4`; budgets=`[16, 64]` chunk=`256` target_tokens=`128`; mode `ROUTE vs frozen SERVE recipe`.

| family | mean teacher_lp | Δ lp | mean tok/s | Δ tok/s | mean wall_ms/prompt | Δ wall | mean est GFLOPs | n |
|--------|-----------------|------|------------|---------|---------------------|--------|-----------------|---|
| H-SERVE | -12.5914 | — | 1227.2 | — | 6 | — | 6.111 | 3 |
| H-SROUTE | -10.8930 | +1.6984 | 2190.7 | +963.5 | 13 | +7 | 38.918 | 3 |

**Decision: PROMOTE (ROUTE not dominated by SERVE)**

Tip H-EARLY / util H-SERVE / H-ROUTE unchanged unless PROMOTE replaces SERVE as serving default.

Commands: `npm run nano:sroute` → `npm run nano:sroute:report`.
