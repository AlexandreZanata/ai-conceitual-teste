# H-ASYNC smoke — overlap TOP cache build with PIN train

Sequential H-PIN = full top-k cache then pinned train (`e2e = cache_build + train`).
H-ASYNC = 1-deep CUDA pipeline: build record i+1 while training step i.
Kill if quality < PIN−ε or no end-to-end wall win.
Recipe: `seq_lo=6`, `n_stages=4`, `steps=30`, `top_k=64`, mode `1-deep pipeline build(i+1)∩PIN train(i)`.

| family | mean teacher_lp | Δ lp | mean e2e_wall_s | Δ e2e | mean ms/step | n |
|--------|-----------------|------|-----------------|-------|--------------|---|
| H-PIN | -16.6988 | — | 0.263 | — | 6.1 | 3 |
| H-ASYNC | -16.6988 | +0.0000 | 0.384 | +0.121 | 12.8 | 3 |

**Decision: KILL (no end-to-end train wall win vs H-PIN)**

Train I/O util on PIN axis — tip STAG / TOP / PIN unchanged as tips.

Commands: `npm run nano:async` → `npm run nano:async:report`.
