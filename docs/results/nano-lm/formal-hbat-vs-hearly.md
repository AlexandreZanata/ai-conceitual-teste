# Formal H-BAT vs serial H-EARLY (batched throughput)

Source: `results/nano-lm/formal-hbat/formal.json`
Wall clock: 7.8s

Shared formal B2 + formal EARLY exit knobs. Fit≠eval (`eval_prompts`).
Mode: `tip-exit knobs; n=1 near-greedy`. Kill if |Δlp| > ε or no tok/s win.
n_prompts=8.

| family | mean teacher_lp | Δ lp | mean tok/s | Δ tok/s | mean wall_ms/prompt | n |
|--------|-----------------|------|------------|---------|---------------------|---|
| H-EARLY | -16.1953 | — | 602.5 | — | 17 | 3 |
| H-BAT | -16.1953 | +0.0000 | 2886.3 | +2283.9 | 3 | 3 |

**Decision:** PROMOTE (batched throughput vs serial EARLY)

Throughput util — does not replace H-EARLY single-prompt tip.

Commands: `npm run nano:formal:hbat` → `npm run nano:formal:hbat:report`.
