# Formal H-EARLY vs B4 (confidence early-exit)

Source: `results/nano-lm/formal-hearly/formal.json`
Wall clock: 46.7s

Shared B2 ckpts. Evolve early-exit knobs. Fit≠eval.
Kill if quality < B4−ε or no wall win vs B4.

| family | mean teacher_lp | mean wall_ms | Δ lp vs B4 | n |
|--------|-----------------|--------------|------------|---|
| B4 | -14.4943 | 82 | — | 3 |
| H-EARLY | -11.8304 | 65 | +2.6639 | 3 |

**Decision:** PROMOTE (quality@wall vs B4)

Commands: `npm run nano:formal:hearly` → `npm run nano:formal:hearly:report`.
