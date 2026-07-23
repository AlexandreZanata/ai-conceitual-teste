# H-ELI smoke vs H-SEL

Strong elitism: keep `elite_k=2` unchanged each generation; mutate only the remaining slots from elites.

| family | mean teacher_lp | Δ vs H-SEL | diversity collapse | n |
|--------|-----------------|------------|--------------------|---|
| H-SEL | −17.01 | — | — | 3 |
| H-ELI | −17.42 | **−0.41** | no | 3 |
| B2 | −17.09 | — | — | 3 |

**Decision: KILL / hold** — diversity did **not** collapse (pairwise L2 stayed high), but teacher_lp ≤ H-SEL. Strong elitism did not help the claim metric at smoke budget.

Commands: `npm run nano:eli` → `npm run nano:matrix:report`.  
Artifacts: `results/nano-lm/student-matrix/eli_smoke.json`, `HELI_seed*_train.json`.
