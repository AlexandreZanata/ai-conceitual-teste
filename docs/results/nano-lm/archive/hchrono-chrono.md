# H-ABS-CHRONO smoke — acausal KD soft-label time shuffle (**KILL**)

> Smoke **KILL**. Do not claim code IQ from shuffled soft-label KD. Tooling purged.

Wave X absurd sandbox: fine-tune B2 with story-teacher soft KD where soft-label time order is shuffled (acausal targets); infer causal EARLY on prog@128. ≠ CKD code soft-KD revive; ≠ MIXD CE mix. Parent = bare H-EARLY(B2).

Frozen: ε=0.05; steps=30; T=2; α=0.5; seeds=3; max_new=32; mean_shuffle_tv≈0.851.

**Decision: KILL (code_lp not up: -17.9939 ≤ parent -16.2692)**

## Arms

| arm | mean story_lp | mean code_lp | mean wall_ms | n |
|-----|---------------|--------------|--------------|---|
| H-EARLY B2 | -14.8854 | -16.2692 | 13 | 12 |
| H-ABS-CHRONO | -14.7710 | -17.9939 | 9 | 12 |

## Lesson

Time-shuffled soft KD **did** apply acausal targets (shuffle TV≈0.85) and slightly helped story_lp / wall, but **lowered** `code_teacher_lp` (Δ≈−1.72). Acausal soft-label order is not a free code-IQ lift vs causal EARLY(B2). Next E.1: **H-ABS-MIRROR** (anti-teacher margin) — not another CKD/CHRONO soft-KD variant.

Commands (purged): were `npm run nano:chrono` / `nano:chrono:report`.
