# H-XOV smoke vs H-SEL

Uniform weight crossover: truncate to top half, blend two parent `state_dict`s
(per-tensor coin flip), then mutate — vs mutate-only H-SEL.

| family | mean teacher_lp | Δ vs H-SEL | diversity collapse | n |
|--------|-----------------|------------|--------------------|---|
| H-SEL | −17.01 | — | — | 3 |
| H-XOV | −16.28 | **+0.73** | no | 3 |
| B2 | −17.09 | — | — | 3 |

**Decision: PROMOTE (beats H-SEL, diversity ok)** — tentative smoke. Diversity
rose across gens; `crossover=1` logged in train meta. Formal reverse-check still
required before claims.

Commands: `npm run nano:xov` → `npm run nano:matrix:report`.  
Artifacts: `results/nano-lm/student-matrix/xov_smoke.json`, `HXOV_seed*_train.json`.
