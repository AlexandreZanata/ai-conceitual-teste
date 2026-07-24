# H-STEP smoke — early-stop KD vs H-CURL2

CURL2 recipe (seq_lo=6); stop when fit-prompt teacher_lp plateaus.
Same max step budget as tip. Kill if claim lp worse than tip.

| family | mean teacher_lp | Δ vs CURL2 | mean steps_run | mean wall_ms | n |
|--------|-----------------|------------|----------------|--------------|---|
| H-CURL2 | -17.2317 | — | 30 | 74 | 3 |
| H-STEP | -17.4659 | -0.2341 | 23 | 42 | 3 |

**Decision: KILL (worse than H-CURL2 tip)**

Commands: `npm run nano:step` → `npm run nano:step:report`.
