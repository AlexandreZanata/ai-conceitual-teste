# H-ANN smoke vs KD-cos

Annealing schedule (linear decay of LR **and** KD temperature) vs cosine LR decay with fixed temperature.

| family | mean teacher_lp | Δ vs KD-cos | Δ vs B2 | n |
|--------|-----------------|-------------|---------|---|
| B2 (fixed LR/temp) | −17.09 | — | — | 3 |
| KD-cos | −17.39 | — | −0.30 | 3 |
| H-ANN | −17.38 | **+0.008** | −0.29 | 3 |

**Decision: PROMOTE (smoke, tentative)** — beats cosine KD on teacher mean log-prob. Both scheduled variants underperform fixed-LR B2 on this smoke slice; treat as schedule ablation only until formal.

Schedules logged in `*_train.json` (`lr_hist`, `temp_hist`). Commands: `npm run nano:ann` → `npm run nano:matrix:report`.  
Artifacts: `results/nano-lm/student-matrix/ann_smoke.json`.
