# Formal H-DEB vs B2 (dual student; teacher picks)

Source: `results/nano-lm/formal-hdeb/formal.json`
Wall clock: 149.4s

Equal budget: 120 steps, seeds 0–2, eval_prompts (batch=2 for dual VRAM).
Kill if ≤ B2.

| family | mean teacher_lp | Δ vs B2 | mean wall_ms | n |
|--------|-----------------|---------|--------------|---|
| B2 | -14.9626 | — | 70 | 3 |
| H-DEB | -14.9740 | -0.0115 | 67 | 3 |

**Decision:** KILL (≤ B2)

Commands: `npm run nano:formal:hdeb` → `npm run nano:formal:hdeb:report`.
