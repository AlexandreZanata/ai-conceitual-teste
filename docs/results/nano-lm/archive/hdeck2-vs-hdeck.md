# H-DECK2 smoke — top_k ∈ {1,2,3} ablation vs H-DECK (k=2)

Equal pop×gens; only teacher rescore width (`top_k`) varies.
Kill if best k ≤ H-DECK (k=2).

| top_k | mean teacher_lp | Δ vs k=2 | wall_save | n |
|-------|-----------------|----------|-----------|---|
| 1 | -16.3215 | -0.5130 | yes | 3 |
| 2 | -15.8086 | — | yes | 3 |
| 3 | -17.3228 | -1.5142 | yes | 3 |

**Decision: KILL (best k ≤ H-DECK k=2)**

Best top_k: 2.

Commands: `npm run nano:deck2` → `npm run nano:deck2:report`.
