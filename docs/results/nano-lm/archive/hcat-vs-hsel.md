# H-CAT smoke vs H-SEL

Catastrophe: every `cat_every` gens keep top-1 and refill the rest with
random immigrants; other gens use steady H-SEL truncation+mutate.

| family | mean teacher_lp | Δ vs H-SEL | n |
|--------|-----------------|------------|---|
| H-SEL | −17.01 | — | 3 |
| H-CAT | −17.54 | **−0.53** | 3 |
| B2 | −17.09 | — | 3 |

**Decision: KILL / hold** — steady H-SEL wins at smoke budget.
`catastrophe_log` shows gen=1 with 3 immigrants (pop=4, keep=1); params ≤5M.

Commands: `npm run nano:cat` → `npm run nano:matrix:report`.  
Artifacts: `results/nano-lm/student-matrix/cat_smoke.json`, `HCAT_seed*_train.json`.
