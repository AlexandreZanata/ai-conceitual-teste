# H-RPS smoke vs H-SEL

Rock–paper–scissors niches: each individual carries niche ∈ {0,1,2};
selection fitness = probe CE + bonus × (# opponents this niche beats).
Niche mutates with probability `niche_mut_p`. Kill if population collapses
to one niche.

| family | mean teacher_lp | Δ vs H-SEL | n | niche_collapsed |
|--------|-----------------|------------|---|-----------------|
| H-SEL | −17.01 | — | 3 | — |
| H-RPS | −17.52 | **−0.51** | 3 | 2/3 seeds |
| B2 | −17.09 | — | 3 | — |

**Decision: KILL** — collapsed to 1 niche on 2/3 seeds (kill criterion hit);
also ≤ H-SEL on teacher_lp. `niche_hist` shows diversity drop within 3 gens;
params ≤5M.

Commands: `npm run nano:rps` → `npm run nano:matrix:report`.  
Artifacts: `results/nano-lm/student-matrix/rps_smoke.json`, `HRPS_seed*_train.json`.
