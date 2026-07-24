# Formal H-CURL — seq_lo ∈ {8,16,32} vs H-CUR (lo=16)

Source: `results/nano-lm/formal-hcurl/formal.json`
Wall clock: 423.8s

Equal budget: 120 steps, seeds 0–2, eval_prompts; n_stages=3.
Kill if best seq_lo ≤ H-CUR (lo=16).

| seq_lo | mean teacher_lp | Δ vs lo=16 | n |
|--------|-----------------|------------|---|
| 8 | -13.3636 | +0.1277 | 3 |
| 16 | -13.4913 | — | 3 |
| 32 | -13.4926 | -0.0013 | 3 |

**Decision:** PROMOTE (best seq_lo=8 > H-CUR)

Best seq_lo: 8.

Commands: `npm run nano:formal:curl` → `npm run nano:formal:curl:report`.
