# H-TAX smoke vs H-SEL

Wealth tax: each gen, scale top-half elite float weights by `(1−τ)` (`τ=0.05`),
then breed from those taxed elites (same truncation width as H-SEL).

| family | mean teacher_lp | Δ vs H-SEL | n |
|--------|-----------------|------------|---|
| H-SEL | −17.01 | — | 3 |
| H-TAX | −17.08 | **−0.08** | 3 |
| B2 | −17.09 | — | 3 |

**Decision: KILL / hold** — H-SEL wins at smoke budget; taxing elites does not help.
`tau`, `elite_k`, and `taxed_per_gen` logged; student params ≤5M.

Commands: `npm run nano:tax` → `npm run nano:matrix:report`.  
Artifacts: `results/nano-lm/student-matrix/tax_smoke.json`, `HTAX_seed*_train.json`.
