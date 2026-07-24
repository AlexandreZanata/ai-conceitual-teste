# Formal H-MPE vs H-MINP (evolved min_p gene)

Source: `results/nano-lm/formal-hmpe/formal.json`
Wall clock: 64.7s

Shared B2 ckpts; fit≠eval; evolve min_p+T/top_p vs grid tip.
Kill if quality < tip−ε or no wall win.

| family | mean teacher_lp | mean wall_ms | Δ lp vs tip | n |
|--------|-----------------|--------------|-------------|---|
| H-MINP | -13.3209 | 63 | — | 3 |
| H-MPE | -12.0037 | 64 | +1.3172 | 3 |

**Decision:** KILL (no speedup vs H-MINP)

Commands: `npm run nano:formal:mpe` → `npm run nano:formal:mpe:report`.
