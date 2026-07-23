# Formal H-DECKL vs B4 (DECK search + lat-aware claim)

Source: `results/nano-lm/formal-hdeckl/formal.json`
Wall clock: 33.0s

Shared B2 ckpts. pop=8 gens=12 top_k=1 λ=0.15. Fit≠eval.
Kill if dominated on Pareto by B4.

| family | mean teacher_lp | mean wall_ms | Δ lp vs B4 | n |
|--------|-----------------|--------------|------------|---|
| B4 | -14.4943 | 84 | — | 3 |
| H-DECKL | -11.7313 | 75 | +2.7630 | 3 |

**Decision:** PROMOTE (Pareto-dominates B4)

Commands: `npm run nano:formal:hdeckl` → `npm run nano:formal:hdeckl:report`.
