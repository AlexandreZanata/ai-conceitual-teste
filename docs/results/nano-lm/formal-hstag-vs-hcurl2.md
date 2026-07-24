# Formal H-STAG — n_stages ∈ {2,3,4} under seq_lo=6

Source: `results/nano-lm/formal-hstag/formal.json`
Wall clock: 257.3s

Equal budget; seq_lo=6. Tip stages=3 reuses formal H-CURL2 lo=6 ckpts.
Kill if best ≤ tip.

| n_stages | mean teacher_lp | Δ vs stages=3 | n |
|----------|-----------------|---------------|---|
| 2 | -13.9724 | -0.6298 | 3 |
| 3 | -13.3427 | — | 3 |
| 4 | -13.2803 | +0.0623 | 3 |

**Decision:** PROMOTE (best n_stages=4 > H-CURL2 tip)

Best n_stages: 4.

Commands: `npm run nano:formal:hstag` → `npm run nano:formal:hstag:report`.
