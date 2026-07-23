# H-NIC smoke vs H-SEL

Fitness sharing: `shared = raw − α · mean_j 1/(1+L2)` (crowding penalty), then
top-half truncation + mutate (same scaffold as H-SEL).

| family | mean teacher_lp | Δ vs H-SEL | diversity↑ | n |
|--------|-----------------|------------|------------|---|
| H-SEL | −17.01 | — | — | 3 |
| H-NIC | −17.01 | **0.00** | yes (all seeds) | 3 |
| B2 | −17.09 | — | — | 3 |

**Decision: KILL / hold** — diversity rose (`niche_alpha=0.001`), but teacher_lp did
not beat H-SEL (tie at smoke budget). Kill criterion “quality↓ / no gain vs H-SEL” hit.

Commands: `npm run nano:nic` → `npm run nano:matrix:report`.  
Artifacts: `results/nano-lm/student-matrix/nic_smoke.json`, `HNIC_seed*_train.json`.
