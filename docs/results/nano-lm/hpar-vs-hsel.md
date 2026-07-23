# H-PAR smoke vs H-SEL

Parasite genome: each individual carries a tiny vector `p`; selection fitness =
`host_fit + α·tanh(mean(p))` (`α=0.5`). Truncation uses selection fitness;
host CE fitness is logged separately. Dominates if parent sets diverge in
>50% of gens.

| family | mean teacher_lp | Δ vs H-SEL | n |
|--------|-----------------|------------|---|
| H-SEL | −17.01 | — | 3 |
| H-PAR | −17.64 | **−0.63** | 3 |
| B2 | −17.09 | — | 3 |

**Decision: KILL (parasite dominates)** — diverge_rate > 0.5 on seed 1; also no
host gain vs H-SEL. `steal_alpha`, `claims_per_gen`, `parasite_dominates` logged;
params ≤5M.

Commands: `npm run nano:par` → `npm run nano:matrix:report`.  
Artifacts: `results/nano-lm/student-matrix/par_smoke.json`, `HPAR_seed*_train.json`.
