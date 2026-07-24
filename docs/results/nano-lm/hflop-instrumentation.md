# H-FLOP smoke — tokens/s + estimated GFLOPs alongside wall

Instrumentation on B2 student: B3 AR vs frozen H-EARLY tip genes.
Est. FLOPs = 2·N·Σ(seq_len) (uncached); kill gate = metrics present.
Future speed claims should prefer GFLOPs when wall is GPU-noisy.

| family | mean teacher_lp | mean wall_ms | mean tok/s | mean est GFLOPs | n |
|--------|-----------------|--------------|------------|-----------------|---|
| B3 | -17.0918 | 77 | 619.6 | 6.751 | 3 |
| H-EARLY | -15.9694 | 45 | 720.7 | 8.930 | 3 |

**Decision: PROMOTE (FLOP+tps metrics live)**

Commands: `npm run nano:flop` → `npm run nano:flop:report`.
