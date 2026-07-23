# H-DECK smoke vs H-DEC (proxy rank + teacher top-k)

Search: student self-logprob ranks pop; teacher rescores top-k only.
Claim: teacher_lp on eval; wall_save = fewer teacher forwards than full H-DEC.

| family | mean teacher_lp | Δ vs H-DEC | wall_save | n |
|--------|-----------------|------------|-----------|---|
| H-DEC | -16.9235 | — | — | 3 |
| H-DECK | -16.4637 | +0.4598 | yes | 3 |

**Decision: PROMOTE (quality@budget vs H-DEC)**

Commands: `npm run nano:deck` → `npm run nano:deck:report`.
