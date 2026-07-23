# H-BAL smoke vs B2 / H-SEL

Baldwin effect: lifetime CE GD on phenotype; Darwinian inherit genotype only.

| family | mean teacher_lp | Δ vs B2 | train notes | n seeds |
|--------|-----------------|---------|-------------|---------|
| B2 | −17.09 | — | KD 30 steps | 3 |
| H-SEL | −17.01 | +0.08 | pop=4, gens=3 (smoke PROMOTE; formal reversed) | 3 |
| H-BAL | −17.39 | −0.30 | pop=4, gens=3, lifetime_steps=2 | 3 |

**Decision: KILL / hold** — does not beat B2 on teacher mean log-prob at smoke budget. Lifetime CE improves probe fitness vs pure H-SEL (−10.62 vs −10.81) but does not improve the claim metric vs B2.

Commands: `npm run nano:bal` → `npm run nano:matrix:report`.  
Artifacts: `results/nano-lm/student-matrix/bal_smoke.json`, `HBAL_seed*_train.json`.
