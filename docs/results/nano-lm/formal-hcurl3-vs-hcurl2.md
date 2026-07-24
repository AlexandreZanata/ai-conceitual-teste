# Formal H-CURL3 — micro seq_lo ∈ {5,6,7} vs tip lo=6

Source: `results/nano-lm/formal-hcurl3/formal.json`
Wall clock: 238.6s

Equal budget; n_stages=3. Tip lo=6 reuses formal H-CURL2 ckpts.
Kill if best ≤ tip.

| seq_lo | mean teacher_lp | Δ vs lo=6 | n |
|--------|-----------------|-----------|---|
| 5 | -13.5983 | -0.2556 | 3 |
| 6 | -13.3427 | — | 3 |
| 7 | -13.4810 | -0.1384 | 3 |

**Decision:** KILL (best seq_lo ≤ H-CURL2 lo=6)

Best seq_lo: 6.

Commands: `npm run nano:formal:curl3` → `npm run nano:formal:curl3:report`.
