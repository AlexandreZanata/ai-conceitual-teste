# H-GLD smoke vs H-FIT

Goldilocks fitness: raw metric is teacher_lp (same as H-FIT); selection uses
`−|raw−mid|/width` with `mid=−17`, `width=2` so mid-band is rewarded and
extremes punished. Checkpoint keeps best raw teacher_lp. Kill if ≤ max-lp (H-FIT).

| family | mean teacher_lp | Δ vs H-FIT | n |
|--------|-----------------|------------|---|
| H-FIT | −16.83 | — | 3 |
| H-GLD | −16.83 | **0.00** | 3 |
| H-SEL | −17.01 | — | 3 |
| B2 | −17.09 | — | 3 |

**Decision: KILL / hold** — no gain vs max-lp H-FIT at smoke budget.
`gld_mid`, `gld_width`, `gld_scores_per_gen` logged; params ≤5M.

Commands: `npm run nano:gld` → `npm run nano:matrix:report`.  
Artifacts: `results/nano-lm/student-matrix/gld_smoke.json`, `HGLD_seed*_train.json`.
