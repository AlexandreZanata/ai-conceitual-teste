# Formal H-POOL vs cold H-DECKL (cross-seed warm-start)

Source: `results/nano-lm/formal-hpool/formal.json`
Wall clock: 52.9s

Shared B2 ckpts. pop=8 gens=12 top_k=1. Leave-one-out gene pool.
Kill if ≤ cold H-DECKL.

| family | mean teacher_lp | Δ vs cold | mean wall_ms | n |
|--------|-----------------|-----------|--------------|---|
| H-DECKL | -11.7313 | — | 76 | 3 |
| H-POOL | -11.6938 | +0.0375 | 70 | 3 |

**Decision:** PROMOTE (beats cold H-DECKL)

Commands: `npm run nano:formal:hpool` → `npm run nano:formal:hpool:report`.
