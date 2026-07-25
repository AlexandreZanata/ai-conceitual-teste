# H-CTX smoke — chunked-KV long window (**KILL**)

> Smoke **KILL**. Do not claim C1@256 via chunked-KV prefill alone. Tooling purged.

Wave X C1: chunked KV prefill under H-EARLY at L=256 vs serial EARLY at L=128 (chunk=64). Not blind ood_long (XFER2) and not naive RAG prepend. Domain gate = `code_teacher_lp` on the C0 task prompt; ε=0.05; δ wall=1.0.

**Decision: KILL (code_lp@C1 −16.9977 < C0−ε −16.3192)**

## Arms (task-aligned dual lp)

| arm | mean story_teacher_lp | mean code_teacher_lp | mean wall_ms | n |
|-----|-----------------------|----------------------|--------------|---|
| C0 serial@128 | -14.8854 | -16.2692 | 22 | 12 |
| C1 chunked-KV@256 | -14.7418 | -16.9977 | 13 | 12 |

## Lesson

Chunked-KV prefill at L=256 held wall (even ↓) and story≈C0, but **lowered** `code_teacher_lp` (Δ ≈ −0.73 vs C0). Long-window quality needs a stronger operator than block prefill alone (see H-QCTX / hierarchical / sliding-attn crop — not another pack letter, not RAG prepend).

Frozen before smoke: parent=C0 serial@128; mechanism=chunked-KV@256 B=64; ε=0.05; δ=1.0; seeds=3; max_new=32; prog pack.

Commands (purged): were `npm run nano:ctx` / `nano:formal:hctx`.
