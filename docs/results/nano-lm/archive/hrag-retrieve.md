# H-RAG smoke — curated retrieve @ decode (KILL)

> Smoke **KILL**. Do not claim curated RAG @ decode. Tooling purged.

Wave X knowledge without weight grow: prepend top-k curated programming chunks at decode (weights frozen). Parent = bare H-EARLY on prog@128. Domain signal = `code_teacher_lp` on the **bare** task prompt (H-TCHR teacher `bigcode/tiny_starcoder_py`). δ wall = 0.50.

**Decision: KILL (domain signal not ↑; story floor also failed on task-aligned text lp)**

## Arms (task-aligned dual lp)

| arm | mean story_teacher_lp | mean code_teacher_lp | mean wall_ms | mean hit | n |
|-----|-----------------------|----------------------|--------------|----------|---|
| H-EARLY (bare) | -14.8854 | -16.2692 | 22 | 0.000 | 12 |
| H-RAG | -14.9673 | -17.0266 | 10 | 0.210 | 12 |

## Lesson

Jaccard top-2 prepend (1105 programming chunks, k=2, 256-char windows) retrieved with mean hit≈0.21 but **lowered** `code_teacher_lp` (Δ ≈ −0.76). Wall was within δ (actually lower — early-exit artifact). Do not revive naive chunk-prepend RAG without a new operator (inject layer / better retriever / H-CTX window mechanism).

Frozen before smoke: parent=EARLY; ε=strict code_lp↑; δ=0.50 wall; L=128; seeds=3; max_new=32.

Commands (purged): were `npm run nano:rag` / `nano:formal:hrag`.
