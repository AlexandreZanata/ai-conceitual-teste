# H-DECP smoke vs GLOBAL + B4 (per-prompt gene bank)

Bank: one evolved gene per fit prompt. Claim: proxy pick from bank.
GLOBAL: single gene evolved on all fit prompts. Kill if ≤ GLOBAL or B4.

| family | mean teacher_lp | mean wall_ms | Δ lp vs B4 | n |
|--------|-----------------|--------------|------------|---|
| B4 | -17.0202 | 55 | — | 3 |
| GLOBAL | -16.7857 | 47 | +0.2345 | 3 |
| H-DECP | -16.2125 | 49 | +0.8077 | 3 |

**Decision: PROMOTE (per-prompt bank > global and B4)**

Commands: `npm run nano:decp` → `npm run nano:decp:report`.
