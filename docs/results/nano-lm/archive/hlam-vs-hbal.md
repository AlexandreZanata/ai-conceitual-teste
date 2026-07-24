# H-LAM smoke vs H-BAL

Lamarckian write-back: same lifetime CE GD as H-BAL, but inherit **phenotype** (learned weights) into the next generation.

| family | mean teacher_lp | Δ vs H-BAL | Δ vs B2 | unstable | n |
|--------|-----------------|------------|---------|----------|---|
| B2 | −17.09 | — | — | no | 3 |
| H-BAL | −17.39 | — | −0.30 | no | 3 |
| H-LAM | −17.00 | **+0.39** | +0.09 | no | 3 |

**Decision: PROMOTE (smoke)** — stable and beats H-BAL on teacher mean log-prob. Also edges B2 on this smoke slice (tentative; small pop/gens).

**Formal reverse:** `docs/results/nano-lm/formal-hlam-vs-hbal.md` — **KILL**
(Δ−0.12 vs H-BAL; also ≤ B2; stable).

Commands: `npm run nano:lam` → `npm run nano:formal:hlam` → report.  
Artifacts: `results/nano-lm/student-matrix/lam_smoke.json`; formal under
`results/nano-lm/formal-hlam-b2/`.
