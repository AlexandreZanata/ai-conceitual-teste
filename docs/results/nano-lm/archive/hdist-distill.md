# H-DIST smoke — shared-vocab code distill (**KILL**)

> Smoke **KILL**. Do not claim code IQ from shared-vocab Neo KD on curated prog. Tooling purged.

Wave X code intelligence: continue B2 with **shared-vocab** soft KD from `EleutherAI/gpt-neo-125M` (same tokenizer as student) on curated programming windows. Explicitly ≠ CKD cross-tok soft-KD and ≠ MIXD hard-CE mix. Gate: `code_teacher_lp` ↑ vs EARLY/B2 parent and story ≥ parent−ε; student ≤5M. Eval code teacher remains `bigcode/tiny_starcoder_py` (H-TCHR).

Frozen: T=2; α=0.5; steps=30×3 seeds; ε=0.05; max_new=32; prog pack; params=3.35M.

**Decision: KILL (code_lp not up: -18.5189 ≤ parent -16.2692)**

## Arms

| arm | mean story_teacher_lp | mean code_teacher_lp | mean wall_ms | n |
|-----|-----------------------|----------------------|--------------|---|
| H-EARLY / B2 parent | -14.8854 | -16.2692 | 14 | 12 |
| H-DIST | -14.6398 | -18.5189 | 10 | 12 |

## Lesson

Shared-vocab KD from GPT-Neo-125M on curated prog **still lowered** `code_teacher_lp` under the StarCoder eval teacher (Δ ≈ −2.25 vs EARLY/B2) while story held. Aligning BPE indices is not enough when the distill teacher is not a code specialist matched to the eval metric. Next: E.1 sandbox (one absurd/QI ID) — not MIXD CE mix, not CKD cross-tok soft-KD, not another Neo-on-prog KD claim.

Commands (purged): were `npm run nano:dist` / `nano:formal:hdist*`.
