# Formal H-THIN vs H-CURL (thin student + EARLY genes)

Source: `results/nano-lm/formal-hthin/formal.json`
Wall clock: 74.1s

Thin CURL train (≤3M); claim with formal EARLY tip genes. Fit≠eval.
Kill if quality < CURL−ε or no wall win on same decode.

| family | mean teacher_lp | mean wall_ms | Δ lp vs CURL | n |
|--------|-----------------|--------------|--------------|---|
| H-CURL | -11.0192 | 79 | — | 3 |
| H-THIN | -11.3486 | 67 | -0.3294 | 3 |

**Decision:** KILL (quality drop vs H-CURL)

Commands: `npm run nano:formal:hthin` → `npm run nano:formal:hthin:report`.
