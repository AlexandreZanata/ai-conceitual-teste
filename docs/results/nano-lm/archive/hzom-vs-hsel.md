# H-ZOM smoke vs H-SEL

Zombie reinjection: each gen, bottom-half “dead” weights are reinjected as
`−w + scale·N(0,1)` into half the next population; remaining slots mutate from
top-half parents (H-SEL). Kill if diverge (NaN/Inf) or ≤ H-SEL.

| family | mean teacher_lp | Δ vs H-SEL | n |
|--------|-----------------|------------|---|
| H-SEL | −17.01 | — | 3 |
| H-ZOM | −17.42 | **−0.41** | 3 |
| B2 | −17.09 | — | 3 |

**Decision: KILL / hold** — no diverge; H-SEL wins at smoke budget.
`dead_per_gen` + `diverged=false` logged; params ≤5M.

Commands: `npm run nano:zom` → `npm run nano:matrix:report`.  
Artifacts: `results/nano-lm/student-matrix/zom_smoke.json`, `HZOM_seed*_train.json`.
