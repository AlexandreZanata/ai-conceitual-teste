# Formal H-POOLB vs serial H-POOL (batched throughput)

Source: `results/nano-lm/formal-hpoolb/formal.json`
Wall clock: 13.0s

Left-pad prompts; shared forward per step under frozen POOL tip knobs.
Fit≠eval. Gate: |Δlp| ≤ ε **and** tok/s > serial POOL.
Prompt pack: eval (`n_prompts=8`); mode `POOL tip top_p; n=1 near-greedy`.

| family | mean teacher_lp | Δ lp | mean tok/s | Δ tok/s | mean wall_ms/prompt | n |
|--------|-----------------|------|------------|---------|---------------------|---|
| H-POOL | -12.1488 | — | 738.1 | — | 66 | 3 |
| H-POOLB | -12.1488 | +0.0000 | 3778.4 | +3040.3 | 13 | 3 |

**Decision:** PROMOTE (batched throughput vs serial POOL)

Tip H-POOL search genes unchanged; POOLB is throughput util on quality axis.

Commands: `npm run nano:formal:hpoolb` → `npm run nano:formal:hpoolb:report`.
