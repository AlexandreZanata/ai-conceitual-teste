# H-DECKL smoke vs B4 (DECK search + lat-aware claim)

Search: self-lp proxy + teacher top-k; select by `lp − λ·log1p(wall)`.
Kill if dominated on Pareto (lp↑, wall↓) by B4 / H-CASC.

| family | mean teacher_lp | mean wall_ms | Δ lp vs B4 | n |
|--------|-----------------|--------------|------------|---|
| B4 | -17.0202 | 55 | — | 3 |
| H-DECKL | -16.6512 | 46 | +0.3691 | 3 |

**Decision: PROMOTE (Pareto-dominates B4)**

Commands: `npm run nano:deckl` → `npm run nano:deckl:report`.
