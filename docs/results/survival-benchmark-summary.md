# Survival benchmark summary

> Aggregated from `results/survival/`. Phase 08 timed benches.
> **Smoke protocol:** regenerate with `npm run bench:aggregate` after runs.
> `—` = τ not reached (or recovery undefined). `n/a` = not applicable.

| technique | bench | median time-to-τ (ms) | fitness@budget | AUC | recovery lag (gens) |
|-----------|-------|------------------------|----------------|-----|---------------------|
| R0 | TB-30 | — | -0.6717 | -51.5 | n/a |
| A | TB-30 | 2.5 | -0.269 | -11.07 | n/a |
| B | TB-30 | — | -0.7375 | -27.76 | n/a |
| C | TB-30 | 0.5 | -0.349 | -8.192 | n/a |
| C-L | TB-30 | — | -0.6837 | -26.29 | n/a |
| A+ | TB-30 | 0.5 | -0.3737 | -2.867 | n/a |
| R0 | TB-DRIFT | — | -0.8255 | -79.07 | — |
| C | TB-DRIFT | 1 | -0.5335 | -7.925 | — |
