# H-HOP smoke vs B2 (tiny Hopfield prior)

KD with continuous Hopfield retrieve on hidden states → lm_head.
Kill if no gain vs B2 (deeper AR / fixed KD).

| family | mean teacher_lp | Δ vs B2 | n |
|--------|-----------------|---------|---|
| B2 | -17.0918 | — | 3 |
| H-HOP | -17.0610 | +0.0308 | 3 |

**Decision: PROMOTE (beats B2)**

Commands: `npm run nano:hop` → `npm run nano:hop:report`.
