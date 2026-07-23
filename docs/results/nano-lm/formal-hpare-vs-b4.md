# Formal H-PARE vs B4 (Pareto archive + knee claim)

Source: `results/nano-lm/formal-hpare/formal.json`
Wall clock: 31.6s

Shared B2 ckpts. pop=8 gens=12 top_k=1. Fit≠eval.
Kill if empty front or ≤ B4 / dominated.

| family | mean teacher_lp | mean wall_ms | Δ lp vs B4 | front_n | n |
|--------|-----------------|--------------|------------|---------|---|
| B4 | -14.4943 | 77 | — | — | 3 |
| H-PARE | -12.3529 | 68 | +2.1413 | 3.7 | 3 |

**Decision:** PROMOTE (Pareto-dominates B4)

Commands: `npm run nano:formal:hpare` → `npm run nano:formal:hpare:report`.
