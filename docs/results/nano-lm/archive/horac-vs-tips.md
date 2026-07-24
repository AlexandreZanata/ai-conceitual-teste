# H-ORAC smoke vs H-EARLY × H-DECM (teacher-oracle tip pick)

Decode both frozen tip genes; teacher picks; charge **winner wall only**.
Diagnostic dual-gate bound. Kill if ≤ max tip or no wall win vs faster tip.

| family | mean teacher_lp | mean wall_ms | Δ lp vs max tip | n |
|--------|-----------------|--------------|-----------------|---|
| H-EARLY | -16.5322 | 43 | — | 3 |
| H-DECM | -16.2919 | 216 | — | 3 |
| H-ORAC | -15.9877 | 78 | +0.3042 | 3 |

**Decision: KILL (no dual wall win)**

Commands: `npm run nano:orac` → `npm run nano:orac:report`.
