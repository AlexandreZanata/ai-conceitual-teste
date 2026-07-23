# H-SEA smoke vs H-FIT

Seasons: even gens select by teacher_lp (H-FIT metric); odd gens select by
probe CE (−loss). Equal pop×gens vs fixed H-FIT (always teacher_lp).

| family | mean teacher_lp | Δ vs H-FIT | n |
|--------|-----------------|------------|---|
| H-FIT | −16.83 | — | 3 |
| H-SEA | −17.33 | **−0.50** | 3 |
| H-SEL | −17.01 | — | 3 |
| B2 | −17.09 | — | 3 |

**Decision: KILL / hold** — fixed H-FIT wins at smoke budget.
`season_log` shows `teacher_lp → ce → teacher_lp`; params ≤5M.

Commands: `npm run nano:sea` → `npm run nano:matrix:report`.  
Artifacts: `results/nano-lm/student-matrix/sea_smoke.json`, `HSEA_seed*_train.json`.
