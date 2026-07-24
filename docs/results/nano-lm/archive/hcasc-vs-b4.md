# H-CASC smoke vs B4 (proxy → mid teacher → full)

Cascade: self-lp proxy → short teacher mid_k → full teacher final_k.
Kill if no teacher-forward save vs full H-DEC or ≤ B4.

| family | mean teacher_lp | Δ vs B4 | wall_save | n |
|--------|-----------------|---------|-----------|---|
| B4 | -17.0202 | — | — | 3 |
| H-CASC | -16.9779 | +0.0423 | yes | 3 |

**Decision: PROMOTE (beats B4 @ forward save)**

Commands: `npm run nano:casc` → `npm run nano:casc:report`.
