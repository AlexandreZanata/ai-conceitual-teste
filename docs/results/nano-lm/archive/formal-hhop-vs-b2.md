# Formal H-HOP vs B2 (tiny Hopfield prior)

Source: `results/nano-lm/formal-hhop/formal.json`
Wall clock: 183.7s

Equal budget: KD 120 steps, seeds 0–2, eval_prompts.
Kill if no gain vs B2.

| family | mean teacher_lp | Δ vs B2 | mean wall_ms | n |
|--------|-----------------|---------|--------------|---|
| B2 | -14.6480 | — | 61 | 3 |
| H-HOP | -15.0461 | -0.3981 | 58 | 3 |

**Decision:** KILL (no gain vs B2)

Commands: `npm run nano:formal:hhop` → `npm run nano:formal:hhop:report`.
