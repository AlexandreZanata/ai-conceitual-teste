# H-THIN smoke — thin CURL student + frozen EARLY genes

Train ≤3M student with CURL (lo=8); claim with tip EARLY genes.
Control: H-CURL tip ckpt on the same EARLY decode.
Kill if quality < CURL−ε or no wall win.

| family | mean teacher_lp | mean wall_ms | Δ lp vs CURL | n |
|--------|-----------------|--------------|--------------|---|
| H-CURL | -16.4291 | 54 | — | 3 |
| H-THIN | -16.0549 | 44 | +0.3741 | 3 |

**Decision: PROMOTE (thin CURL + EARLY vs tip)**

Commands: `npm run nano:thin` → `npm run nano:thin:report`.
