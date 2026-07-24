# Formal H-CURD vs H-CURL2 (difficulty curriculum)

Source: `results/nano-lm/formal-hcurd/formal.json`
Wall clock: 70.4s

Equal budget: 120 steps; tip = formal CURL2 lo=6. Fixed seq_len.
Kill if ≤ H-CURL2 tip on teacher_lp.

| family | mean teacher_lp | Δ vs CURL2 | mean wall_ms | n |
|--------|-----------------|------------|--------------|---|
| H-CURL2 | -13.3427 | — | 66 | 3 |
| H-CURD | -14.5071 | -1.1644 | 61 | 3 |

**Decision:** KILL (≤ H-CURL2 tip)

Commands: `npm run nano:formal:hcurd` → `npm run nano:formal:hcurd:report`.
