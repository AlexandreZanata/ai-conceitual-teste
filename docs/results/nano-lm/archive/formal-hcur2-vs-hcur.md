# Formal H-CUR2 — n_stages ∈ {2,3,4,5} vs H-CUR (n=3)

Source: `results/nano-lm/formal-hcur2/formal.json`
Wall clock: 588.1s

Equal budget: 120 steps, seeds 0–2, eval_prompts.
Kill if best n ≤ H-CUR (n=3).

| n_stages | mean teacher_lp | Δ vs n=3 | n |
|----------|-----------------|----------|---|
| 2 | -13.8334 | -0.3059 | 3 |
| 3 | -13.5275 | — | 3 |
| 4 | -13.2577 | +0.2698 | 3 |
| 5 | -13.2558 | +0.2717 | 3 |

**Decision:** PROMOTE (best n_stages=5 > H-CUR)

Best n_stages: 5.

Commands: `npm run nano:formal:cur2` → `npm run nano:formal:cur2:report`.
