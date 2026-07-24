# H-EAR2 smoke — widened early-exit gene vs H-EARLY

Gene adds max_new + conf_metric∈{max_p,margin,entropy}; wider min_new.
Kill if quality < EARLY−ε or no wall win vs H-EARLY.

| family | mean teacher_lp | mean wall_ms | Δ lp vs EARLY | n |
|--------|-----------------|--------------|---------------|---|
| H-EARLY | -16.5322 | 43 | — | 3 |
| H-EAR2 | -16.8138 | 26 | -0.2817 | 3 |

**Decision: KILL (quality drop vs H-EARLY)**

Commands: `npm run nano:ear2` → `npm run nano:ear2:report`.
