# H-ENT2 smoke vs B2

Repair of H-ENT: dual-head KD **without** agreement reward; add
`tv_floor_loss = relu(τ − TV)` (τ=0.02, weight=1.0) to punish head collapse.

| family | mean teacher_lp | Δ vs B2 | mean TV | collapsed | n |
|--------|-----------------|---------|---------|-----------|---|
| B2 | −17.09 | — | — | — | 3 |
| H-ENT (prior) | −16.99 | +0.10 | ~0.005 | **yes** | 3 |
| H-ENT2 | −16.99 | +0.10 | ~0.005 | **yes** | 3 |

**Decision: KILL (collapsed again)** — TV floor did not keep mean TV ≥ τ.
Quality edge vs B2 is irrelevant under the collapse kill gate.
Params ≤5M (~3.36M). Try H-ENT3 (maximize TV) next if revisiting dual heads.

Commands: `npm run nano:ent2` → `npm run nano:matrix:report`.  
Artifacts: `results/nano-lm/student-matrix/ent2_smoke.json`, `HENT2_seed*_train.json`.
