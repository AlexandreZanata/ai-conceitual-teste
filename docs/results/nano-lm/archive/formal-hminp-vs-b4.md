# Formal H-MINP vs B4 (min-p sampling)

Source: `results/nano-lm/formal-hminp/formal.json`
Wall clock: 30.5s

Shared B2 ckpts; fit≠eval; grid min_p∈{0,0.05,0.1,0.2}.
Kill if quality < B4−ε or no wall win.

| family | mean teacher_lp | mean wall_ms | Δ lp vs B4 | n |
|--------|-----------------|--------------|------------|---|
| B4 | -14.4943 | 81 | — | 3 |
| H-MINP | -13.3209 | 61 | +1.1733 | 3 |

**Decision:** PROMOTE (quality@wall vs B4)

Commands: `npm run nano:formal:minp` → `npm run nano:formal:minp:report`.
