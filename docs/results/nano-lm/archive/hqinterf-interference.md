# H-Q-INTERF smoke — story∧code teacher score interference (**KILL**)

> Smoke **KILL**. Do not claim dual-teacher interference from BoN α-commit. Tooling purged.

Wave X QI sandbox: generate **N=4** student EARLY candidates; score each with story + code teachers; commit `argmax α·story_lp+(1−α)·code_lp` (α∈{0.25,0.5,0.75}). Parent = bare H-EARLY n=1 on prog@128. ≠ CKD soft-KD, ≠ MIXD CE mix, ≠ slot-measure.

Frozen: ε=0.05; N_cand=4; alphas=(0.25,0.5,0.75); seeds=3; max_new=32; prog pack; best_α=0.25 (by mean interf_score).

**Decision: KILL (story_lp -15.4650 < parent−ε -14.9354)**

## Arms

| arm | mean story_lp | mean code_lp | mean wall_ms | n |
|-----|---------------|--------------|--------------|---|
| H-EARLY parent | -14.8854 | -16.2692 | 23 | 12 |
| H-Q-INTERF α=0.25 | -15.4650 | -7.9516 | 175 | 12 |

## Lesson

α-weighted dual-teacher BoN **lifted** `code_teacher_lp` a lot (Δ ≈ +8.3 vs parent) but **broke** the dual gate: `story_lp` fell below parent−ε (Δ ≈ −0.58). Constructive interference of score fields is not free when α favors the code teacher — story regress kills the claim. Next E.1: **H-ABS-REV** (time-reversed prefill) — not another dual-score mix / CKD / MIXD.

Commands (purged): were `npm run nano:interf` / `nano:formal:hinterf*`.
