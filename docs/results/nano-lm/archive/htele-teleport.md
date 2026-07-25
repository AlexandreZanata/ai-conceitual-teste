# H-Q-TELE smoke — mid-layer residual RAG teleport (**KILL**)

> Smoke **KILL**. Do not claim mid-layer teleport dual-gate win from wall↓ with identity continuations. Tooling purged.

Wave X QI sandbox: retrieve top-k Jaccard curated chunks, mean-pool student wte embeddings, inject α·v into last-token residual at layer ℓ*=1 only (early layers see task ids; no prompt prepend). ≠ naive RAG; ≠ MEASURE/SLOT commit. Parent = bare H-EARLY on prog@128.

Frozen: ε=0.05; k=2; ℓ*=1; α=1.0; max_new=32; seeds=3; n_chunks=256.

**Decision: KILL (identity vs parent; TELE had no effect)**

## Arms

| arm | mean story_lp | mean code_lp | mean wall_ms | mean gflops | mean hit | n |
|-----|---------------|--------------|--------------|-------------|----------|---|
| H-EARLY bare | -14.8854 | -16.2692 | 22 | 6.501 | 0.000 | 12 |
| H-Q-TELE k=2 ℓ*=1 | -14.8854 | -16.2692 | 9 | 6.501 | 0.143 | 12 |

## Lesson

Retrieve+inject **ran** (hit≈0.14, injects≈6.7/row) and wall↓, but **all 12** greedy continuations matched parent story/code LPs exactly — identity under EARLY. Frozen mid-layer residual teleport of Jaccard wte means is not a free code-IQ lift when argmax paths collapse. Next E.1: **H-Q-WIGNER** (signed top-k logit quasi-prob) — not another residual/RAG inject.

Commands (purged): were `npm run nano:tele` / `nano:tele:report`.
