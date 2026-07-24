# H-PRUN smoke — magnitude prune STAG + recovery vs tip

Prune Linear weights to ~30% sparsity, short masked KD recovery,
claim with frozen EARLY genes. FLOPs scaled by density.
Kill if quality < STAG−ε or no FLOP win vs STAG.

| family | mean teacher_lp | Δ lp | mean wall_ms | mean est GFLOPs | Δ GFLOPs | density | n |
|--------|-----------------|------|--------------|-----------------|----------|---------|---|
| H-STAG | -16.2155 | — | 77 | 8.930 | — | 1.000 | 3 |
| H-PRUN | -15.6751 | +0.5404 | 45 | 6.251 | -2.679 | 0.700 | 3 |

**Decision: PROMOTE (prune+recover vs STAG)**

Note: est. GFLOPs use density scaling (dense CUDA kernels still run). Formal deferred
until sparse-kernel or wall dual gate looks real on fit≠eval.

Commands: `npm run nano:prun` → `npm run nano:prun:report`.
