# Formal H-TYP vs B4 (typical sampling)

Source: `results/nano-lm/formal-htyp/formal.json`
Wall clock: 29.3s

Shared B2 ckpts; fit≠eval; grid mass∈{1,0.9,0.8,0.7}.
Kill if quality < B4−ε or no wall win.

| family | mean teacher_lp | mean wall_ms | Δ lp vs B4 | n |
|--------|-----------------|--------------|------------|---|
| B4 | -14.4943 | 82 | — | 3 |
| H-TYP | -14.5337 | 68 | -0.0394 | 3 |

**Decision:** PROMOTE (quality@wall vs B4)

Commands: `npm run nano:formal:typ` → `npm run nano:formal:typ:report`.
