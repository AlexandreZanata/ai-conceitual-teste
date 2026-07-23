# H-ENT smoke vs B2

Dual-head student (shared body + shared noise + two projections into shared `lm_head`) trained with KD on both heads plus an agreement (symmetric KL) reward.

| family | mean teacher_lp | Δ vs B2 | mean TV (heads) | collapsed | n |
|--------|-----------------|---------|-----------------|-----------|---|
| B2 | −17.09 | — | — | — | 3 |
| H-ENT | −16.99 | +0.10 | ~0.005 | **yes** | 3 |

**Decision: KILL (collapsed to one head)** — agreement reward drove mean total-variation between heads below the floor (0.02). Quality edge vs B2 is irrelevant under the kill gate.

Params ≤5M (~3.36M). Commands: `npm run nano:ent` → `npm run nano:matrix:report`.  
Artifacts: `results/nano-lm/student-matrix/ent_smoke.json`, `HENT_seed*_train.json`.
