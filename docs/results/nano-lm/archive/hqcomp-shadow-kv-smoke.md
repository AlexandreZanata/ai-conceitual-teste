# H-QCOMP smoke — classical-shadow KV sketch

Wave X quantum-*inspired* compression: prefill KV at L=256, project sequence with Rademacher Phi to S=64 slots, decode with compressed past. Parent = serial EARLY at L=128. Not Born-rule attn (H-QCTX), not chunked-KV (H-CTX), not RAG.
Inspiration: `Classical shadows / random ±1 KV projections (H-Q-SHADOW; no quantum hardware)`.
Surrogate: `Prefill KV@T; Phi[T,S]=±1/√S; K_s=K·Phi; keep past length S; recon MSE via K̂=K_s·Phi^T; mem↓ iff nbytes(S)<nbytes(T)`.
Parent recipe: `H-EARLY / PACK tip @128`.
Mode: `QCOMP: classical-shadow KV (≠ Born-rule, ≠ chunked-KV, ≠ RAG)`; mechanism=`shadow KV sketch S=64 @256 vs EARLY @128`; cpu_threads=`14`.

## Teachers

| role | hf_id | params | license |
|------|-------|--------|---------|
| story | `roneneldan/TinyStories-33M` | 33M | TinyStories |
| code | `bigcode/tiny_starcoder_py` | 164000000 | BigCode OpenRAIL-M v1 |

**Decision: PROMOTE (shadow KV sketch; code/story ≥ C0−ε; kv_bytes↓ vs full@L; wall budget OK)**

## Arms

| arm | mean story_lp | mean code_lp | mean wall_ms | kv_bytes | full_kv_bytes | recon_mse | n |
|-----|---------------|--------------|--------------|----------|---------------|-----------|---|
| C0 EARLY@128 | -14.8854 | -16.2692 | 22 | nan | nan | nan | 12 |
| H-QCOMP@256 | -14.5106 | -13.2320 | 9 | 65536 | 289792 | 0.1560 | 12 |

Tips unchanged. Wave X QCOMP (shadow KV).

Commands: `npm run nano:qcomp` → `npm run nano:qcomp:report`.
