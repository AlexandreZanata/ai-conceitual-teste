# Formal H-LOT vs B2 (sparse lottery ticket)

Source: `results/nano-lm/formal-hlot/formal.json`
Wall clock: 190.0s

Equal budget: KD 120 steps, keep_frac=0.3, seeds 0–2, eval_prompts.
Kill if ≤ B2; quality cliff if Δ < −0.5.

| family | mean teacher_lp | Δ vs B2 | mean wall_ms | n |
|--------|-----------------|---------|--------------|---|
| B2 | -14.6480 | — | 77 | 3 |
| H-LOT | -16.1721 | -1.5241 | 59 | 3 |

**Decision:** KILL (quality cliff)

Commands: `npm run nano:formal:hlot` → `npm run nano:formal:hlot:report`.
