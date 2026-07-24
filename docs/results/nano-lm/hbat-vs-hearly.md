# H-BAT smoke — batched multi-prompt EARLY vs serial

Left-pad prompts; one shared forward per step under frozen EARLY tip.
Kill if |Δlp| > ε vs serial or no tok/s win. Throughput ≠ single-prompt wall.
Prompt pack: smoke+fit (`n_prompts=4`); mode `n=1 near-greedy`.

| family | mean teacher_lp | Δ lp | mean tok/s | Δ tok/s | mean wall_ms/prompt | Δ wall | mean est GFLOPs | Δ GFLOPs | n |
|--------|-----------------|------|------------|---------|---------------------|--------|-----------------|----------|---|
| H-EARLY | -14.6404 | — | 566.5 | — | 22 | — | 0.808 | — | 3 |
| H-BAT | -14.6404 | +0.0000 | 1789.8 | +1223.3 | 5 | -17 | 0.808 | +0.000 | 3 |

**Decision: PROMOTE (batched throughput vs serial EARLY)**

Note: smoke uses n=1 near-greedy for lp fidelity; tip EARLY unchanged.
Throughput util — formal only if tip-policy batching stays within ε.

Commands: `npm run nano:bat` → `npm run nano:bat:report`.
