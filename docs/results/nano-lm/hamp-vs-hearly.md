# H-AMP smoke — CUDA AMP decode vs H-EARLY

Same B2 ckpt + frozen EARLY genes; autocast `bf16` matmuls (Q8 redo on CUDA).
Short AMP KD train path exercised; claim is same-ckpt decode.
Kill if quality < EARLY−ε or no wall win vs EARLY.

| family | mean teacher_lp | Δ lp | mean wall_ms | Δ wall | mean est GFLOPs | n |
|--------|-----------------|------|--------------|--------|-----------------|---|
| H-EARLY | -16.5322 | — | 44 | — | 8.930 | 3 |
| H-AMP | -16.5894 | -0.0572 | 50 | +6 | 8.930 | 3 |

**Decision: KILL (quality drop vs H-EARLY)**

Commands: `npm run nano:amp` → `npm run nano:amp:report`.
