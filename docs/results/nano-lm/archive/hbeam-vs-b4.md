# H-BEAM smoke vs B4 (evolved beam search)

Evolve beam_width∈{2..5} + length_penalty; student beam decode.
Kill if quality < B4−ε or no wall win vs B4.

| family | mean teacher_lp | mean wall_ms | Δ lp vs B4 | n |
|--------|-----------------|--------------|------------|---|
| B4 | -17.0202 | 55 | — | 3 |
| H-BEAM | -11.0029 | 82 | +6.0174 | 3 |

**Decision: KILL (no speedup vs B4)**

Δ H-BEAM vs B4 lp: +6.0174.

Commands: `npm run nano:beam` → `npm run nano:beam:report`.
