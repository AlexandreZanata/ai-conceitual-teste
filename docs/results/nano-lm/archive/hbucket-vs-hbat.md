# H-BUCKET smoke — length-banded BAT vs flat H-BAT

Pad only within length bands (`band=4`); shared EARLY tip, n=1 near-greedy.
Kill if |Δlp| > ε vs H-BAT/serial or no tok/s win vs H-BAT.
Prompt pack: `n=1 near-greedy; eval pack` (`n_prompts=8`).

| family | mean teacher_lp | Δ lp vs BAT | mean tok/s | Δ tok/s | mean wall_ms/prompt | Δ wall | n |
|--------|-----------------|-------------|------------|---------|---------------------|--------|---|
| H-EARLY | -14.5917 | — | 605.6 | — | 15 | — | 3 |
| H-BAT | -14.5917 | — | 2966.5 | — | 3 | — | 3 |
| H-BUCKET | -14.5917 | +0.0000 | 2188.6 | -777.8 | 3 | +0 | 3 |

**Decision: KILL (no tok/s win vs H-BAT)**

Note: throughput util deepen of H-BAT; tip EARLY unchanged.
Lesson: on this nano pack (8 prompts, ~2 bands), sequential bucket launches
cost more than saved pad FLOPs — flat H-BAT remains the throughput util.

Commands: `npm run nano:bucket` → `npm run nano:bucket:report`.
