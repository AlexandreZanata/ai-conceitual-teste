# H-SPE smoke vs H-SEL

Island model: 2 islands of size 2; breed within islands; every `migrate_every=2`
gens ring-migrate each island’s top-1 into the destination island’s worst slot.
Equal pop×gens vs single-island H-SEL.

| family | mean teacher_lp | Δ vs H-SEL | n |
|--------|-----------------|------------|---|
| H-SEL | −17.01 | — | 3 |
| H-SPE | −17.23 | **−0.22** | 3 |
| B2 | −17.09 | — | 3 |

**Decision: KILL / hold** — single-island H-SEL wins at smoke budget.
`n_islands`, `migrate_every`, and `migration_log` logged.

Commands: `npm run nano:spe` → `npm run nano:matrix:report`.  
Artifacts: `results/nano-lm/student-matrix/spe_smoke.json`, `HSPE_seed*_train.json`.
