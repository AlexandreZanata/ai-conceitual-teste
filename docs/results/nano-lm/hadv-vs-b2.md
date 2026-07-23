# H-ADV smoke vs B2 (weak discriminator + teacher judge)

KD + weak top-k soft discriminator; claim metric remains teacher_lp.
Kill if mode collapse (entropy drop) or ≤ B2.

| family | mean teacher_lp | Δ vs B2 | mode_collapsed | n |
|--------|-----------------|---------|----------------|---|
| B2 | -17.0918 | — | — | 3 |
| H-ADV | -17.0918 | +0.0000 | no | 3 |

**Decision: KILL (≤ B2)**

Commands: `npm run nano:adv` → `npm run nano:adv:report`.
