# H-Q-ENTPOS smoke — low-rank bilinear pos⊗tok bias (**KILL**)

> Smoke **KILL**. Do not claim entangled-pos dual-gate win from wall↓ with identical text. Tooling purged.

Wave X QI sandbox: add low-rank bilinear pos×tok bias to GPT-Neo attn (rank=8, scale=0.15) — not PHASE rotary / SPIRAL Hilbert. Parent = bare H-EARLY on prog@128. Gate: not collapse, not identity, both lps ≥ parent−ε, (code↑ or wall↓); audit H(attn) + head TV.

Frozen: ε=0.05; rank=8; scale=0.15; H_min=0.75; TV_min=1e-4; max_new=32; seeds=3.

**Decision: KILL (identity vs parent; ENTPOS had no effect)**

## Arms

| arm | mean story_lp | mean code_lp | mean wall_ms | mean H(attn) | mean head_tv | n |
|-----|---------------|--------------|--------------|--------------|--------------|---|
| H-EARLY bare | -14.8854 | -16.2692 | 23 | — | — | 12 |
| H-Q-ENTPOS R=8 | -14.8854 | -16.2692 | 17 | 4.9661 | 0.055163 | 12 |

## Lesson

Bilinear pos⊗tok bias **did not collapse** (H≈4.97, TV≈0.055) and cut wall, but **all 12** greedy continuations matched parent story/code LPs exactly — identity under EARLY. Frozen low-rank entanglement is not a free content–position upgrade when argmax paths collapse. Next E.1: **H-Q-MEASURE** (mid-decode RAG slot commit) — not another pos bias / PHASE / SPIRAL.

Commands (purged): were `npm run nano:entpos` / `nano:formal:hentpos*`.
