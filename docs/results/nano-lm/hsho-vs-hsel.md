# H-SHO smoke vs H-SEL

Shock: after plain mutate, reinit one random layer (block / embed / head)
from a freshly initialized student; rest of tensors keep the mutated weights.
Control = plain mutate (H-SEL).

| family | mean teacher_lp | Δ vs H-SEL | n |
|--------|-----------------|------------|---|
| H-SEL | −17.01 | — | 3 |
| H-SHO | −16.96 | **+0.05** | 3 |
| B2 | −17.09 | — | 3 |

**Decision: PROMOTE** (tentative) — beats plain mutate at smoke budget.
`shocks_per_gen` logs per-child layer prefixes; params ≤5M.

**Formal reverse:** `docs/results/nano-lm/formal-hsho-vs-b2.md` — **KILL**
(Δ−1.86 vs B2).

Commands: `npm run nano:sho` → `npm run nano:formal:hsho` → report.  
Artifacts: `results/nano-lm/student-matrix/sho_smoke.json`; formal under
`results/nano-lm/formal-hsho-b2/`.
