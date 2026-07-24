# Formal H-CUR vs B2 (length-curriculum KD)

Source: `results/nano-lm/formal-hcur/formal.json`
Wall clock: 255.8s

Equal budget: 120 steps, seeds 0–2, eval_prompts, seq_lo→seq_hi ramp.
Kill if ≤ B2.

| family | mean teacher_lp | Δ vs B2 | mean wall_ms | n |
|--------|-----------------|---------|--------------|---|
| B2 | -14.6480 | — | 71 | 3 |
| H-CUR | -13.4537 | +1.1943 | 62 | 3 |

**Decision:** PROMOTE (beats B2)

Commands: `npm run nano:formal:cur` → `npm run nano:formal:cur:report`.
