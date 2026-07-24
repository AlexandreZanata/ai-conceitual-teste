# H-POOLB smoke — batched multi-prompt POOL vs serial

Left-pad prompts; one shared forward per step under frozen POOL tip knobs.
Kill if |Δlp| > ε vs serial or no tok/s win. Throughput ≠ single-prompt wall.
Prompt pack: smoke+fit (`n_prompts=4`); mode `POOL tip top_p; n=1 near-greedy`.

| family | mean teacher_lp | Δ lp | mean tok/s | Δ tok/s | mean wall_ms/prompt | Δ wall | mean est GFLOPs | Δ GFLOPs | n |
|--------|-----------------|------|------------|---------|---------------------|--------|-----------------|----------|---|
| H-POOL | -11.0690 | — | 670.1 | — | 53 | — | 6.537 | — | 3 |
| H-POOLB | -11.0690 | +0.0000 | 2386.6 | +1716.4 | 14 | -39 | 6.537 | +0.000 | 3 |

**Decision: PROMOTE (batched throughput vs serial POOL)**

Note: smoke uses n=1 near-greedy for lp fidelity; tip POOL search unchanged.
Throughput util on quality@wall axis — formal only if dual gate looks real.

Commands: `npm run nano:poolb` → `npm run nano:poolb:report`.
