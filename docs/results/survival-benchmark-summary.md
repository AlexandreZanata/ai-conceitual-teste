# Survival benchmark summary

> Aggregated from `results/survival/`. Phase 08 timed benches.
> **Smoke protocol:** regenerate with `npm run bench:aggregate` after runs.
> `—` = τ not reached (or recovery undefined). `n/a` = not applicable.

| technique | bench | median time-to-τ (ms) | fitness@budget | AUC | recovery lag (gens) |
|-----------|-------|------------------------|----------------|-----|---------------------|
| R0 | TB-30 | — | -0.6717 | -25.43 | n/a |
| A | TB-30 | 2 | -0.269 | -11.07 | n/a |
| B | TB-30 | — | -0.7375 | -27.76 | n/a |
| C | TB-30 | 0.5 | -0.349 | -3.842 | n/a |
| C-L | TB-30 | — | -0.6837 | -26.29 | n/a |
| A+ | TB-30 | 0.5 | -0.3737 | -2.867 | n/a |
| R0 | TB-60 | — | -0.798 | -62.12 | n/a |
| A | TB-60 | 1 | -0.6808 | -34.07 | n/a |
| B | TB-60 | — | -0.7985 | -63.12 | n/a |
| C | TB-60 | 4.5 | -0.5702 | -28.87 | n/a |
| C-L | TB-60 | — | -0.7983 | -62.48 | n/a |
| A+ | TB-60 | 2 | -0.5678 | -14.36 | n/a |
| R0 | TB-120 | — | -0.8565 | -126.8 | — |
| A | TB-120 | — | -0.848 | -124.1 | — |
| B | TB-120 | — | -0.8328 | -124.8 | — |
| C | TB-120 | — | -0.835 | -123.9 | — |
| C-L | TB-120 | — | -0.8343 | -124.7 | — |
| A+ | TB-120 | — | -0.8222 | -124.5 | — |
| R0 | TB-DRIFT | — | -0.8255 | -79.07 | — |
| A | TB-DRIFT | 1 | -0.5082 | -6.921 | — |
| B | TB-DRIFT | — | -0.804 | -79.2 | — |
| C | TB-DRIFT | 1 | -0.5335 | -7.925 | — |
| C-L | TB-DRIFT | — | -0.8023 | -79.31 | — |
| A+ | TB-DRIFT | 2 | -0.516 | -10.59 | — |
