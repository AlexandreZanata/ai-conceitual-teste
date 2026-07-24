# H-HIB smoke vs H-SEL

Hibernation: every `hib_every` gens skip probe CE and select on
`parent_fit × decay`; other gens use full eval (steady H-SEL). Checkpoint
quality always uses true CE of the selected elite.

| family | mean teacher_lp | Δ vs H-SEL | n |
|--------|-----------------|------------|---|
| H-SEL | −17.01 | — | 3 |
| H-HIB | −17.42 | **−0.41** | 3 |
| B2 | −17.09 | — | 3 |

**Decision: KILL / hold** — full-eval H-SEL wins at smoke budget (stale
inherited fitness does not beat steady selection). `hibernate_log` shows
gen=1 skipped 4 evals; params ≤5M.

Commands: `npm run nano:hib` → `npm run nano:matrix:report`.  
Artifacts: `results/nano-lm/student-matrix/hib_smoke.json`, `HHIB_seed*_train.json`.
