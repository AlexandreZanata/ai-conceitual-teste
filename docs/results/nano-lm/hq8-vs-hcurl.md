# H-Q8 smoke — INT8 dynamic quant + frozen EARLY genes

Inference-only `quantize_dynamic` (qint8 Linear) on H-CURL ckpt;
claim with tip EARLY genes. Dynamic kernels are CPU-backed;
control stays on tip device (CUDA when available).
Kill if quality < CURL−ε or no wall win.

| family | mean teacher_lp | mean wall_ms | Δ lp vs CURL | n |
|--------|-----------------|--------------|--------------|---|
| H-CURL | -16.4291 | 77 | — | 3 |
| H-Q8 | -16.3101 | 212 | +0.1189 | 3 |

**Decision: KILL (no wall win vs H-CURL)**

Commands: `npm run nano:q8` → `npm run nano:q8:report`.
