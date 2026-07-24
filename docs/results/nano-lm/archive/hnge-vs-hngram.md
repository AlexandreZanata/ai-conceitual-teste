# H-NGE smoke vs H-NGRAM (evolved ngram gene)

Evolve ngram_size + T/top_p with latency-aware fitness; claim vs grid H-NGRAM.
Kill if quality < tip−ε or no wall win vs H-NGRAM.

| family | mean teacher_lp | mean wall_ms | Δ lp vs tip | n |
|--------|-----------------|--------------|-------------|---|
| H-NGRAM | -16.4875 | 44 | — | 3 |
| H-NGE | -16.5717 | 43 | -0.0842 | 3 |

**Decision: KILL (quality drop vs H-NGRAM)**

Commands: `npm run nano:nge` → `npm run nano:nge:report`.
