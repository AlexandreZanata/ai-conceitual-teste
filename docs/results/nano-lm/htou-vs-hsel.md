# H-TOU smoke vs H-SEL

Tournament selection (`k=3`) instead of top-half truncation on the H-SEL
scaffold (probe CE fitness, mutate winners).

| family | mean teacher_lp | Δ vs H-SEL | n |
|--------|-----------------|------------|---|
| H-SEL | −17.01 | — | 3 |
| H-TOU | −17.42 | **−0.41** | 3 |
| B2 | −17.09 | — | 3 |

**Decision: KILL / hold** — teacher_lp ≤ H-SEL at equal pop×gens smoke budget.
Parent indices logged in `parents_per_gen`; `select=tournament`, `tournament_k=3`.

Commands: `npm run nano:tou` → `npm run nano:matrix:report`.  
Artifacts: `results/nano-lm/student-matrix/tou_smoke.json`, `HTOU_seed*_train.json`.
