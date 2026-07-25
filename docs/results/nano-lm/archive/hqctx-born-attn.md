# H-QCTX smoke — Born-rule amplitude attention (**KILL**)

> Smoke **KILL**. Do not claim long-L code quality from Born-rule attn alone. Tooling purged.

Wave X quantum-*inspired* context (H-Q-AMP classical surrogate under **H-QCTX**): replace softmax with Born-rule amplitudes (`ψ = score/‖score‖₂`, `attn = ψ²`) under H-EARLY at L=256 vs serial C0 EARLY at L=128. Not chunked-KV (H-CTX) and not RAG prepend.

Inspiration: QubitCache-class / Born-rule amplitude attention (no quantum hardware).  
Parent recipe: H-EARLY / PACK tip @128.  
Frozen: ε=0.05; H_min=0.75; wall_slack=50ms; seeds=3; max_new=32; prog pack.

**Decision: KILL (code_lp@L256 −17.5353 < C0−ε −16.3192)**

## Arms

| arm | mean story_lp | mean code_teacher_lp | mean wall_ms | mean H(attn) | mean PR | n |
|-----|---------------|----------------------|--------------|--------------|---------|---|
| C0 EARLY@128 | -14.8854 | -16.2692 | 22 | — | — | 12 |
| H-QCTX@256 | -15.4671 | -17.5353 | 19 | 5.0047 | 110.39 | 12 |

## Lesson

Born-rule attention **did not collapse** (H≈5.0, PR≫1) and even held wall (↓ vs C0), but **lowered** `code_teacher_lp` at L=256 (Δ ≈ −1.27 vs C0−ε). Amplitude remapping of softmax is not enough for C1 code quality — need stronger long-context ops (hierarchical / QCOMP shadow / critical-KV **H-Q-QUBITKV**), not another attn renormalization.

Commands (purged): were `npm run nano:qctx` / `nano:qctx:report` / `nano:formal:hqctx*`.
