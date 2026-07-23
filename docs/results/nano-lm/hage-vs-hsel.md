# H-AGE smoke vs H-SEL

ALPS-lite: 2 age layers with limits `[2, 1e9]`; breed within layers; inject
`immigrants_per_gen=1` random student (age 0) replacing the worst each generation.
Equal pop×gens vs H-SEL (wall-matched smoke).

| family | mean teacher_lp | Δ vs H-SEL | n |
|--------|-----------------|------------|---|
| H-SEL | −17.01 | — | 3 |
| H-AGE | −17.42 | **−0.41** | 3 |
| B2 | −17.09 | — | 3 |

**Decision: KILL / hold** — flat H-SEL wins at smoke budget.
`age_layers`, `age_limits`, and `immigrant_counts` logged (1 immigrant/gen).

Commands: `npm run nano:age` → `npm run nano:matrix:report`.  
Artifacts: `results/nano-lm/student-matrix/age_smoke.json`, `HAGE_seed*_train.json`.
