# H-ABS-MIRROR — anti-teacher (1−p) margin (**KILL**)

> Formal **KILL** after smoke provisional PROMOTE. Do not claim dual-gate win from code↑ with story regress. Tooling purged.

Wave X absurd sandbox: fine-tune B2 with story-teacher soft KD plus margin vs anti-teacher (1−p): CE+KL(s‖p)+β·relu(m−(KL(s‖anti)−KL(s‖p))). ≠ CKD/CHRONO revive; ≠ ENT dual-head. Parent = bare H-EARLY(B2).

Frozen: ε=0.05; steps=30; T=2; α=0.5; β=0.5; m=0.05; seeds=3; max_new=32.

## Smoke (provisional PROMOTE)

| arm | mean story_lp | mean code_lp | mean wall_ms | mean TV_anti | n |
|-----|---------------|--------------|--------------|--------------|---|
| H-EARLY B2 | -14.8854 | -16.2692 | 14 | 0.000 | 12 |
| H-ABS-MIRROR | -13.2780 | -12.8675 | 9 | 0.077 | 12 |

Smoke decision: PROMOTE (code↑ Δ≈+3.40, story↑; TV_anti≈0.077; kl_gap diagnostic ≪0).

## Formal (KILL)

| arm | mean story_lp | mean code_lp | mean wall_ms | mean TV_anti | n |
|-----|---------------|--------------|--------------|--------------|---|
| H-EARLY B2 | -10.3233 | -14.1457 | 15 | 0.000 | 12 |
| H-ABS-MIRROR | -12.9699 | -10.7355 | 11 | 0.308 | 12 |

**Decision: KILL (story_lp -12.9699 < parent−ε -10.3733)**

## Lesson

Mirror margin **did** move decode (code↑ on smoke+formal) but formal **story_lp** regressed past ε — dual gate fails. Anti-teacher (1−p) aux is not a free code-IQ lift without story HOLD. kl_gap stayed largely negative (batchmean KL scale / dense anti). Next: **Wave X E.1 ordered catalog exhausted** through MIRROR — propose a new H-ID or HOLD absurd track (GENQ-ABS already KILL).

Commands (purged): were `npm run nano:mirror` / `nano:formal:hmirror*`.
