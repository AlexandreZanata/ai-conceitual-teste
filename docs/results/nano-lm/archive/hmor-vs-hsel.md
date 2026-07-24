# H-MOR smoke vs H-SEL

Soft mortality: cull bottom quartile (`mortality_k=1` for pop=4) before
truncation breed on the H-SEL scaffold.

| family | mean teacher_lp | Δ vs H-SEL | n |
|--------|-----------------|------------|---|
| H-SEL | −17.01 | — | 3 |
| H-MOR | −17.27 | **−0.27** | 3 |
| B2 | −17.09 | — | 3 |

**Decision: KILL / hold** — no-cull H-SEL wins at smoke budget.
`mortality_k` and `culled_per_gen` logged.

Commands: `npm run nano:mor` → `npm run nano:matrix:report`.  
Artifacts: `results/nano-lm/student-matrix/mor_smoke.json`, `HMOR_seed*_train.json`.
