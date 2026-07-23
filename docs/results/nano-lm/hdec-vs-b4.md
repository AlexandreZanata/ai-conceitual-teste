# H-DEC smoke vs B4 (fixed BoN)

Evolve decode genes `{temperature, top_p, N, K, B, H, use_mae}` on frozen B2 student; fitness = teacher log-prob. Claim row uses holdout eval at `max_new=32` (same as B4).

| family | mean teacher_lp | Δ vs B4 | n seeds |
|--------|-----------------|---------|---------|
| B4 (fixed BoN n=4, T=0.8, p=0.9) | −17.02 | — | 3 |
| H-DEC (evolved knobs) | −16.92 | **+0.10** | 3 |

**Decision: PROMOTE (smoke)** — beats fixed BoN/B4 on teacher mean log-prob. Treat as tentative (small pop/gens; search used `max_new=16`).

Best genes (all chose BoN, not MAE):

| seed | eval_lp | gene |
|------|---------|------|
| 0 | −17.16 | T≈1.30, p≈0.88, n=4 |
| 1 | −16.63 | T≈0.47, p≈0.73, n=2 |
| 2 | −16.98 | T≈1.33, p≈0.68, n=3 |

Commands: `npm run nano:dec` → `npm run nano:matrix:report`.  
Artifacts: `results/nano-lm/student-matrix/dec_smoke.json`, `HDEC_seed*_train.json`.
