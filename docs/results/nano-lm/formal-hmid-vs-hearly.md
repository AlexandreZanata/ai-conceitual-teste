# Formal H-MID vs H-EARLY (mid exit + warm-start)

Source: `results/nano-lm/formal-hmid/formal.json`
Wall clock: 50.7s

Fit≠eval; min_new∈{4,8}, n=1, tip warm-start. Kill if lp < tip−ε or GFLOPs ≥ tip.

| family | mean teacher_lp | Δ lp | mean wall_ms | mean est GFLOPs | Δ GFLOPs | n |
|--------|-----------------|------|--------------|-----------------|----------|---|
| H-EARLY | -11.8304 | — | 74 | 19.142 | — | 3 |
| H-MID | -12.3390 | -0.5086 | 61 | 11.614 | -7.528 | 3 |

**Decision:** KILL (quality drop vs H-EARLY)

Commands: `npm run nano:formal:hmid` → `npm run nano:formal:hmid:report`.
