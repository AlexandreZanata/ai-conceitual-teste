# H-JOINT smoke — joint curriculum ∪ early-exit gene

Bank train `(seq_lo,n_stages)`; evolve joint early gene on bank ckpts.
Kill if ≤ CURL default-decode or ≤ H-EARLY@B2 (free lunch / paste).

| family | mean teacher_lp | mean wall_ms | Δ vs CURL | Δ vs EARLY | n |
|--------|-----------------|--------------|-----------|------------|---|
| H-CURL | -16.7160 | 50 | — | — | 3 |
| H-EARLY | -16.5322 | 43 | — | — | 3 |
| H-JOINT | -16.7689 | 42 | -0.0529 | -0.2367 | 3 |

**Decision: KILL (≤ CURL default decode)**

Commands: `npm run nano:joint` → `npm run nano:joint:report`.
