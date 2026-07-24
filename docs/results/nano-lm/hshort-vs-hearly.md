# H-SHORT smoke — two-phase short draft vs H-EARLY

Force short `draft_max` → stop if student conf high; else continue with EARLY exit.
Kill if quality < EARLY−ε or dominated on (wall, GFLOPs).

| family | mean teacher_lp | Δ lp | mean wall_ms | Δ wall | mean est GFLOPs | Δ GFLOPs | n |
|--------|-----------------|------|--------------|--------|-----------------|----------|---|
| H-EARLY | -16.5322 | — | 43 | — | 8.930 | — | 3 |
| H-SHORT | -16.5322 | +0.0000 | 41 | -2 | 8.930 | +0.000 | 3 |

**Decision: PROMOTE (adaptive short draft vs EARLY)**

Note: identical lp + GFLOPs vs tip means draft stop rarely shortened sequences;
wall Δ is tiny (~2ms). Formal only if FLOP/wall dual gate looks real.

Commands: `npm run nano:short` → `npm run nano:short:report`.
