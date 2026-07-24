# H-ANTI smoke vs H-SEL

Anti-selection: each generation, clone + mutate only the *worst* half
(`max(1, n//2)`), inverse of H-SEL top-half truncation. Equal pop×gens.

| family | mean teacher_lp | Δ vs H-SEL | n |
|--------|-----------------|------------|---|
| H-SEL | −17.01 | — | 3 |
| H-ANTI | −17.64 | **−0.63** | 3 |
| B2 | −17.09 | — | 3 |

**Decision: KILL / hold** — H-SEL (and B2) win at smoke budget; anti-selection hurts.
`select=anti_worst_half` and `parents_per_gen` logged; student params ≤5M.

Commands: `npm run nano:anti` → `npm run nano:matrix:report`.  
Artifacts: `results/nano-lm/student-matrix/anti_smoke.json`, `HANTI_seed*_train.json`.
