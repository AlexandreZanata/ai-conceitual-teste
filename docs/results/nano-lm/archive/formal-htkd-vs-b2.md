# Formal H-TKD vs B2 (top-k sparse KD)

Source: `results/nano-lm/formal-htkd/formal.json`
Wall clock: 217.9s

Equal budget: 120 steps, seeds 0–2, eval_prompts, k=32.
Kill if ≤ B2.

| family | mean teacher_lp | Δ vs B2 | mean wall_ms | n |
|--------|-----------------|---------|--------------|---|
| B2 | -14.6480 | — | 68 | 3 |
| H-TKD | -16.6784 | -2.0304 | 63 | 3 |

**Decision:** KILL (≤ B2)

Commands: `npm run nano:formal:htkd` → `npm run nano:formal:htkd:report`.
