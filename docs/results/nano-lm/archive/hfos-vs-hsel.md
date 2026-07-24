# H-FOS smoke vs H-SEL

Fossil vault: non-parent (bottom-half) lineages are archived each gen; every
`resurrect_every=2` gens the oldest fossil replaces the worst newborn.
Equal pop×gens vs H-SEL (no-resurrect control).

| family | mean teacher_lp | Δ vs H-SEL | n |
|--------|-----------------|------------|---|
| H-SEL | −17.01 | — | 3 |
| H-FOS | −17.01 | **0.00** | 3 |
| B2 | −17.09 | — | 3 |

**Decision: KILL / hold** — no gain vs no-resurrect H-SEL at smoke budget.
`resurrect_log` + `vault_final` logged; params ≤5M.

Commands: `npm run nano:fos` → `npm run nano:matrix:report`.  
Artifacts: `results/nano-lm/student-matrix/fos_smoke.json`, `HFOS_seed*_train.json`.
