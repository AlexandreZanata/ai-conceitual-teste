# H-XOV smoke vs H-SEL

Uniform weight crossover: truncate to top half, blend two parent `state_dict`s
(per-tensor coin flip), then mutate — vs mutate-only H-SEL.

| family | mean teacher_lp | Δ vs H-SEL | diversity collapse | n |
|--------|-----------------|------------|--------------------|---|
| H-SEL | −17.01 | — | — | 3 |
| H-XOV | −16.28 | **+0.73** | no | 3 |
| B2 | −17.09 | — | — | 3 |

**Decision: PROMOTE (beats H-SEL, diversity ok)** — tentative smoke. Diversity
rose across gens; `crossover=1` logged in train meta.

**Formal reverse:** `docs/results/nano-lm/formal-hxov-vs-b2.md` — **KILL**
(Δ−1.65 vs B2; no collapse).

Commands: `npm run nano:xov` → `npm run nano:formal:hxov` → report.  
Artifacts: `results/nano-lm/student-matrix/xov_smoke.json`; formal under
`results/nano-lm/formal-hxov-b2/`.
