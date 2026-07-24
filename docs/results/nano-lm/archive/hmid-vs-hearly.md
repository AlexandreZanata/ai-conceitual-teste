# H-MID smoke — mid min_new {4,8} + tip warm-start vs H-EARLY

Between EARF (FLOP tie) and EXIT (quality cliff): n=1, no min_new=2/12.
Kill if quality < EARLY−ε or est_gflops ≥ EARLY tip.

| family | mean teacher_lp | Δ lp | mean wall_ms | mean est GFLOPs | Δ GFLOPs | n |
|--------|-----------------|------|--------------|-----------------|----------|---|
| H-EARLY | -16.5322 | — | 77 | 8.930 | — | 3 |
| H-MID | -16.5504 | -0.0182 | 46 | 6.751 | -2.179 | 3 |

**Decision: PROMOTE (mid exit FLOP win vs H-EARLY)**

Commands: `npm run nano:mid` → `npm run nano:mid:report`.
