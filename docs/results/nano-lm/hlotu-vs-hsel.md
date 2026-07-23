# H-LOTU smoke vs H-SEL

Underdog lottery: each gen the worst individual is replaced by an exact clone
of the elite, then H-SEL top-half truncation breed proceeds. Equal pop×gens.

| family | mean teacher_lp | Δ vs H-SEL | n |
|--------|-----------------|------------|---|
| H-SEL | −17.01 | — | 3 |
| H-LOTU | −17.27 | **−0.27** | 3 |
| B2 | −17.09 | — | 3 |

**Decision: KILL / hold** — H-SEL wins at smoke budget; free elite clone does not help.
`gifts_per_gen` as `[underdog, elite]` logged; params ≤5M.

Commands: `npm run nano:lotu` → `npm run nano:matrix:report`.  
Artifacts: `results/nano-lm/student-matrix/lotu_smoke.json`, `HLOTU_seed*_train.json`.
