# H-ENT3 smoke vs B2

Repair of H-ENT/H-ENT2: KD on **mixed** dual-head logits plus a disagreement
bonus (`loss = KD(mix) − λ·TV`, λ=0.1) to maximize head separation.

| family | mean teacher_lp | Δ vs B2 | mean TV | collapsed | mode_chaos | n |
|--------|-----------------|---------|---------|-----------|------------|---|
| B2 | −17.09 | — | — | — | — | 3 |
| H-ENT | −16.99 | +0.10 | ~0.005 | **yes** | — | 3 |
| H-ENT2 | −16.99 | +0.10 | ~0.005 | **yes** | no | 3 |
| H-ENT3 | −16.99 | +0.10 | ~0.005 | **yes** | no | 3 |

**Decision: KILL (collapsed)** — maximizing TV failed; mean TV stayed ≪ 0.02.
No mode chaos (TV ≪ 0.9). Shared-body dual heads still collapse under smoke KD.
Params ≤5M (~3.36M). Archive dual-head line unless architecture changes.

Commands: `npm run nano:ent3` → `npm run nano:matrix:report`.  
Artifacts: `results/nano-lm/student-matrix/ent3_smoke.json`, `HENT3_seed*_train.json`.
