# Formal H-CASC vs B4 (proxy → mid teacher → full)

Source: `results/nano-lm/formal-hcasc/formal.json`
Wall clock: 38.0s

Shared B2 KD ckpts. pop=8 gens=12 mid_k=3 final_k=1. Fit≠eval.
Kill if no teacher-forward save vs full H-DEC or ≤ B4.

| family | mean teacher_lp | Δ vs B4 | mean wall_ms | wall_save | n |
|--------|-----------------|---------|--------------|-----------|---|
| B4 | -14.4943 | — | 76 | — | 3 |
| H-CASC | -12.2209 | +2.2734 | 184 | yes | 3 |

**Decision:** PROMOTE (beats B4 @ forward save)

Commands: `npm run nano:formal:hcasc` → `npm run nano:formal:hcasc:report`.
