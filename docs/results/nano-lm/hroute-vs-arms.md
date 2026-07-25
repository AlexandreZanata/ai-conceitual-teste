# H-ROUTE smoke — short→GALL, long→GRAPHF vs single arms

Controls: pure H-GALL and pure H-GRAPHF on the same long prompts / budgets. H-ROUTE uses GALL on short budgets and GRAPHF/KV on long (`max_new > thr`). Kill if dominated by either arm on (lp, wall).
Prompt pack: `n_prompts=4`; budgets=`[16, 64]` chunk=`256` target_tokens=`128`; mode `short→GALL; long→GRAPHF/KV vs pure arms`.

| family | mean teacher_lp | Δ lp vs best | mean tok/s | mean wall_ms/prompt | Δ wall vs best | mean est GFLOPs | n |
|--------|-----------------|--------------|------------|---------------------|----------------|-----------------|---|
| H-GALL | -12.5914 | — | 1085.5 | 8 | — | 6.111 | 3 |
| H-GRAPHF | -10.4872 | — | 2012.0 | 19 | — | 43.431 | 3 |
| H-ROUTE | -10.8930 | -0.4059 | 2174.4 | 13 | +5 | 38.918 | 3 |

**Decision: PROMOTE (length-budget router not dominated)**

(Δ tok/s vs max arm: +162.3)

Tip H-EARLY / H-SERVE unchanged unless PROMOTE. Length-budget router.

Commands: `npm run nano:route` → `npm run nano:route:report`.
