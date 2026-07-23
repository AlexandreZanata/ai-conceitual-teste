# Formal H-DECP vs B4 + GLOBAL (per-prompt gene bank)

Source: `results/nano-lm/formal-hdecp/formal.json`
Wall clock: 105.8s

Shared B2 ckpts. Bank on fit; claim on eval via proxy pick. Fit≠eval.
Kill if ≤ GLOBAL or B4.

| family | mean teacher_lp | mean wall_ms | Δ lp vs B4 | n |
|--------|-----------------|--------------|------------|---|
| B4 | -14.4943 | 78 | — | 3 |
| GLOBAL | -11.9640 | 88 | +2.5302 | 3 |
| H-DECP | -12.2269 | 150 | +2.2673 | 3 |

**Decision:** KILL (≤ global gene)

Commands: `npm run nano:formal:hdecp` → `npm run nano:formal:hdecp:report`.
