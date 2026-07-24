# H-BAND smoke vs H-CASC / H-DECK (UCB1 gene arms)

Fixed gene arms; UCB1 allocates teacher scores (no mutate pop).
Pull budget matched to H-CASC mid+final teacher scores.
Kill if ≤ max(H-DECK, H-CASC).

| family | mean teacher_lp | mean teacher_fwd | n |
|--------|-----------------|------------------|---|
| H-DECK | -16.8536 | 4 | 3 |
| H-CASC | -16.9779 | 12 | 3 |
| H-BAND | -17.0053 | 12 | 3 |

**Decision: KILL (≤ H-DECK / H-CASC)**

Commands: `npm run nano:band` → `npm run nano:band:report`.
