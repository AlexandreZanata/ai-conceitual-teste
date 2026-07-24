# H-FIT smoke vs H-SEL

Claim-aligned fitness: same pop×gens mutate scaffold as H-SEL, but fitness =
teacher mean log-prob of short AR completions (`fitness_kind=teacher_lp`), not
probe CE.

| family | mean teacher_lp | Δ vs H-SEL | Δ vs B2 | n |
|--------|-----------------|------------|---------|---|
| H-SEL | −17.01 | — | +0.08 | 3 |
| H-FIT | −16.83 | **+0.18** | **+0.26** | 3 |
| B2 | −17.09 | — | — | 3 |

**Decision: PROMOTE (beats H-SEL)** — tentative smoke. Addresses formal H-SEL
reverse (probe CE ≠ claim metric).

**Formal reverse:** `docs/results/nano-lm/formal-hfit-vs-b2.md` — **KILL**
(overfit + Δ−1.84 vs B2; holdout fit≠eval).

Commands: `npm run nano:fit` → `npm run nano:formal:hfit` → report.  
Artifacts: `results/nano-lm/student-matrix/fit_smoke.json`; formal under
`results/nano-lm/formal-hfit-b2/`.
