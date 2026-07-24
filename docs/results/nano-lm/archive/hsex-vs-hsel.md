# H-SEX smoke vs H-SEL

Mate choice: truncation parents (top half), then for each child pick mate
maximizing shifted `(fit_i × fit_j × L2)`; uniform weight blend then mutate
(same crossover primitive as H-XOV; pairing differs from random).

| family | mean teacher_lp | Δ vs H-SEL | n |
|--------|-----------------|------------|---|
| H-SEL | −17.01 | — | 3 |
| H-SEX | −17.06 | **−0.05** | 3 |
| B2 | −17.09 | — | 3 |

**Decision: KILL / hold** — H-SEL wins at smoke budget (also below H-XOV random pairing).
`mate_choice=fit_x_l2` and `pairs_per_gen` logged; student params ≤5M.

Commands: `npm run nano:sex` → `npm run nano:matrix:report`.  
Artifacts: `results/nano-lm/student-matrix/sex_smoke.json`, `HSEX_seed*_train.json`.
