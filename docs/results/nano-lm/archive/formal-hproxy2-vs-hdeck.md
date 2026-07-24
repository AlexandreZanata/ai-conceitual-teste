# Formal H-PROXY2 vs H-DECK (CE proxy vs self-lp)

Source: `results/nano-lm/formal-hproxy2/formal.json`
Wall clock: 56.0s

Shared B2 KD ckpts. pop=8 gens=12 top_k=1. Fit≠eval prompts.
Kill if ≤ H-DECK quality@forwards.

| family | mean teacher_lp | Δ vs H-DECK | mean wall_ms | mean fwd | n |
|--------|-----------------|-------------|--------------|----------|---|
| H-DECK | -11.7313 | — | 181 | 24 | 3 |
| H-PROXY2 | -11.8399 | -0.1086 | 169 | 24 | 3 |

**Decision:** KILL (≤ H-DECK quality@forwards)

Commands: `npm run nano:formal:hproxy2` → `npm run nano:formal:hproxy2:report`.
