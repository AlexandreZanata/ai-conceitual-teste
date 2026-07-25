# H-CKD smoke — soft-KD from code teacher (**KILL**)

> Smoke **KILL**. Do not claim code IQ from cross-tokenizer soft-KD alone. Tooling purged.

Wave X code intelligence: fine-tune B2 with soft labels from frozen `bigcode/tiny_starcoder_py` on curated programming text (top-k mapped by decoded string → student vocab). Explicitly ≠ MIXD hard-CE curriculum mix. Gate: `code_teacher_lp` ↑ vs EARLY parent **and** story tip ≥ STAG′−ε.

**Decision: KILL (code_lp not up: -19.2446 ≤ parent -16.2692; teacher=bigcode/tiny_starcoder_py)**

## Arms

| arm | mean story_lp (prog) | mean code_teacher_lp | mean story tip | mean wall_ms | n |
|-----|----------------------|----------------------|----------------|--------------|---|
| H-EARLY parent | -10.1603 | -16.2692 | -17.0918 | 15 | 12 |
| H-CKD | -8.7271 | -19.2446 | -16.6348 | 9 | 12 |

## Lesson

Cross-tokenizer soft-KD (T=2, α=0.5, top_k=16, 30 curated prog steps × 3 seeds) **lowered** `code_teacher_lp` (Δ ≈ −2.98 vs EARLY parent) while slightly improving prog story_lp / tip. Soft-label map from StarCoder → GPT-Neo student vocab is not a free code-IQ lift; next code track needs a stronger op (shared-vocab distill **H-DIST**, or different teacher alignment) — not another MIXD CE mix.

Frozen before smoke: parent=H-EARLY on B2; mechanism=cross-tok soft KD; ε=0.05; STAG′=−12.49; seeds=3; max_new=32; prog pack.

Commands (purged): were `npm run nano:ckd` / `nano:ckd:report` / `nano:formal:hckd*`.
