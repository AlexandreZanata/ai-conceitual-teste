# H-SYM smoke vs H-SEL

Obligate pair: only individuals with fitness strictly above the population mean
may breed; consecutive eligible indices form pairs; children = blend + mutate
(H-XOV primitive). If <2 eligible, sterile fallback mutates the current best.

| family | mean teacher_lp | Δ vs H-SEL | n |
|--------|-----------------|------------|---|
| H-SEL | −17.01 | — | 3 |
| H-SYM | −16.82 | **+0.19** | 3 |
| B2 | −17.09 | — | 3 |

**Decision: PROMOTE (smoke, tentative)** — beats H-SEL at smoke budget.
`pairs_per_gen` + `sterile_gens` logged; params ≤5M. Formal reverse-check recommended.

Commands: `npm run nano:sym` → `npm run nano:matrix:report`.  
Artifacts: `results/nano-lm/student-matrix/sym_smoke.json`, `HSYM_seed*_train.json`.
