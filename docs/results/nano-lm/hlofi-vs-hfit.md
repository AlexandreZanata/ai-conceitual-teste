# H-LOFI smoke vs H-FIT

Low-fidelity fitness: CE-rank the full population, then teacher_lp-rescore
**top-k only** (`k=2`, pop=4). Gate: quality ≥ H-FIT − ε (ε=0.05) **and**
fewer teacher forwards than full H-FIT.

| family | mean teacher_lp | Δ vs H-FIT | teacher_forwards / seed | wall_save | n |
|--------|-----------------|------------|-------------------------|-----------|---|
| H-FIT | −16.83 | — | 24 (full) | — | 3 |
| H-LOFI | −17.26 | **−0.42** | **12** | yes | 3 |
| B2 | −17.09 | — | — | — | 3 |

**Decision: KILL** — wall save hit (12 < 24 forwards) but quality < H-FIT − ε.
`teacher_rescored_k`, `train_wall_s`, `teacher_forwards` logged; params ≤5M.
Do not promote cheap CE pre-rank at this smoke budget.

Commands: `npm run nano:lofi` → `npm run nano:matrix:report`.  
Artifacts: `results/nano-lm/student-matrix/lofi_smoke.json`, `HLOFI_seed*_train.json`.
