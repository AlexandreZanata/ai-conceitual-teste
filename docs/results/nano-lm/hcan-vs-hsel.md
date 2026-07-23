# H-CAN smoke vs H-SEL

Cannibalism: each gen, fitness winner copies loser’s GPT-Neo LayerNorm
(`ln_*`) weight/bias tensors, then H-SEL top-half truncation breed.

| family | mean teacher_lp | Δ vs H-SEL | n |
|--------|-----------------|------------|---|
| H-SEL | −17.01 | — | 3 |
| H-CAN | −17.01 | **0.00** | 3 |
| B2 | −17.09 | — | 3 |

**Decision: KILL / hold** — no gain vs H-SEL at smoke budget; no NaN.
`cannibal=winner_copies_loser_ln`, `pairs_per_gen`, `had_nan=false` logged; params ≤5M.

Commands: `npm run nano:can` → `npm run nano:matrix:report`.  
Artifacts: `results/nano-lm/student-matrix/can_smoke.json`, `HCAN_seed*_train.json`.
