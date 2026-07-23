# H-POOL smoke vs cold H-DECKL (cross-seed warm-start)

Cold H-DECKL builds a gene pool; each seed warm-starts from others.
Kill if ≤ cold H-DECKL at equal pop×gens.

| family | mean teacher_lp | Δ vs cold | mean wall_ms | n |
|--------|-----------------|-----------|--------------|---|
| H-DECKL | -16.6512 | — | 48 | 3 |
| H-POOL | -15.5365 | +1.1147 | 44 | 3 |

**Decision: PROMOTE (beats cold H-DECKL)**

Commands: `npm run nano:pool` → `npm run nano:pool:report`.
