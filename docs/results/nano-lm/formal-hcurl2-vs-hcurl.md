# Formal H-CURL2 — fine seq_lo ∈ {4,6,8,10,12} vs tip lo=8

Source: `results/nano-lm/formal-hcurl2/formal.json`
Wall clock: 409.6s

Equal budget: 120 steps, seeds 0–2, eval_prompts; n_stages=3.
Tip lo=8 reuses formal H-CURL ckpts. Kill if best ≤ tip.

| seq_lo | mean teacher_lp | Δ vs lo=8 | n |
|--------|-----------------|-----------|---|
| 4 | -13.5538 | -0.1902 | 3 |
| 6 | -13.3427 | +0.0210 | 3 |
| 8 | -13.3636 | — | 3 |
| 10 | -13.4742 | -0.1106 | 3 |
| 12 | -13.3970 | -0.0334 | 3 |

**Decision:** PROMOTE (best seq_lo=6 > H-CURL tip)

Best seq_lo: 6.

Commands: `npm run nano:formal:curl2` → `npm run nano:formal:curl2:report`.
