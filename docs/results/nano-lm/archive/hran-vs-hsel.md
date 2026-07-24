# H-RAN smoke vs H-SEL

Linear rank roulette: parent probability ∝ rank (1=worst … n=best) instead of
top-half truncation on the H-SEL scaffold.

| family | mean teacher_lp | Δ vs H-SEL | n |
|--------|-----------------|------------|---|
| H-SEL | −17.01 | — | 3 |
| H-RAN | −17.63 | **−0.63** | 3 |
| B2 | −17.09 | — | 3 |

**Decision: KILL / hold** — truncation H-SEL wins at smoke budget.
`select=rank`; `parents_per_gen` and `parent_ranks_per_gen` logged.

Commands: `npm run nano:ran` → `npm run nano:matrix:report`.  
Artifacts: `results/nano-lm/student-matrix/ran_smoke.json`, `HRAN_seed*_train.json`.
