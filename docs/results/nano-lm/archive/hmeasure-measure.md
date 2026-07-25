# H-Q-MEASURE smoke — mid-decode RAG measurement commit (**KILL**)

> Smoke **KILL**. Do not claim mid-decode measure dual-gate win from wall↓ with code↓. Tooling purged.

Wave X QI sandbox: every τ tokens, measure (sample) one Jaccard slot from K=4 superposition and freeze for τ=8 decode steps (rebuild ctx). ≠ one-shot SLOT claim reuse; ≠ naive RAG PROMOTE. Parent = bare H-EARLY on prog@128.

Frozen: ε=0.05; k=4; τ=8; amp_temp=1.0; max_new=32; seeds=3; n_chunks=256.

**Decision: KILL (code_lp -18.0466 < parent−ε -16.3192)**

## Arms

| arm | mean story_lp | mean code_lp | mean wall_ms | mean switches | mean measures | n |
|-----|---------------|--------------|--------------|---------------|---------------|---|
| H-EARLY bare | -14.8854 | -16.2692 | 22 | 0.00 | 0.00 | 12 |
| H-Q-MEASURE k=4 τ=8 | -14.8789 | -18.0466 | 14 | 0.00 | 1.00 | 12 |

## Lesson

Mid-decode measure **changed** decode (code↓ Δ≈−1.78 vs parent−ε) with wall↓, but EARLY exit kept **measures≈1 / switches=0** — effectively one-shot SLOT/RAG prepend. Periodic commit of Jaccard chunks is not a free code-IQ lift vs bare EARLY. Next E.1: **H-Q-TELE** (inject RAG at mid-layer residual) — not another chunk-bank measure/SLOT.

Commands (purged): were `npm run nano:measure` / `nano:formal:hmeasure*`.
