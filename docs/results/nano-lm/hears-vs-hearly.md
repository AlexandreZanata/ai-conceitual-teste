# H-EARS smoke — scheduled early-exit thr vs H-EARLY

Gene adds len_coef / budget_coef / prompt_ref; thr scales with
prompt length and remaining decode budget each step.
Kill if quality < EARLY−ε or no wall win vs H-EARLY.

| family | mean teacher_lp | mean wall_ms | Δ lp vs EARLY | n |
|--------|-----------------|--------------|---------------|---|
| H-EARLY | -16.5322 | 43 | — | 3 |
| H-EARS | -16.6176 | 44 | -0.0854 | 3 |

**Decision: KILL (quality drop vs H-EARLY)**

Commands: `npm run nano:ears` → `npm run nano:ears:report`.
