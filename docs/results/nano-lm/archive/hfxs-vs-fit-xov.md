# H-FXS smoke vs max(H-FIT, H-XOV)

Champion stack: **H-FIT** teacher_lp fitness + **H-XOV** uniform crossover +
**H-SHO** layer shock after mutate. Parents logged as
`[H-FIT, H-XOV, H-SHO]`.

| family | mean teacher_lp | Δ vs max(FIT,XOV) | n |
|--------|-----------------|-------------------|---|
| H-XOV (best single) | −16.28 | — | 3 |
| H-FIT | −16.83 | — | 3 |
| H-SHO | −16.96 | — | 3 |
| H-FXS | −17.13 | **−0.85** | 3 |
| B2 | −17.09 | — | 3 |

**Decision: KILL / hold** — smoke stack ≤ max(H-FIT, H-XOV); also ≤ B2.
`fitness_kind=teacher_lp`, `crossover=1`, `shocks_per_gen` logged; params ≤5M.
Do not promote the stack at this budget; prefer single operators (esp. H-XOV)
or formal only if a stronger stack variant appears.

Commands: `npm run nano:fxs` → `npm run nano:matrix:report`.  
Artifacts: `results/nano-lm/student-matrix/fxs_smoke.json`, `HFXS_seed*_train.json`.
