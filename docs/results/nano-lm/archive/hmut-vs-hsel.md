# H-MUT smoke vs H-SEL

Adaptive mutate scale via instantaneous 1/5 success rule: after each generation,
`mutate_scale *= 1.2` if best fitness improved, else `/= 1.2` (clipped). Same
truncation + mutate scaffold as fixed-scale H-SEL.

| family | mean teacher_lp | Δ vs H-SEL | n |
|--------|-----------------|------------|---|
| H-SEL | −17.01 | — | 3 |
| H-MUT | −17.42 | **−0.41** | 3 |
| B2 | −17.09 | — | 3 |

**Decision: KILL / hold** — fixed-scale H-SEL wins on teacher_lp at smoke budget.
`mutate_scale_hist` logged (e.g. seed0: 0.02 → 0.024 → 0.02).

Commands: `npm run nano:mut` → `npm run nano:matrix:report`.  
Artifacts: `results/nano-lm/student-matrix/mut_smoke.json`, `HMUT_seed*_train.json`.
