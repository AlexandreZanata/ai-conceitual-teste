# Formal H-NGRAM vs B4 (no-repeat n-gram)

Source: `results/nano-lm/formal-hngram/formal.json`
Wall clock: 29.6s

Shared B2 ckpts; fit≠eval prompts; grid n∈{0,2,3,4}.
Kill if quality < B4−ε or no wall win.

| family | mean teacher_lp | mean wall_ms | Δ lp vs B4 | n |
|--------|-----------------|--------------|------------|---|
| B4 | -14.4943 | 79 | — | 3 |
| H-NGRAM | -14.5187 | 60 | -0.0244 | 3 |

**Decision:** PROMOTE (quality@wall vs B4)

Commands: `npm run nano:formal:ngram` → `npm run nano:formal:ngram:report`.
