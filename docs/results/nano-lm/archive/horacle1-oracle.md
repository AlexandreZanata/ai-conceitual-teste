# H-ABS-ORACLE1 smoke — 1-bit hash side channel vs RAG (**KILL**)

> Smoke **KILL**. Do not claim 1-bit oracle steers as well as RAG under dual gate. Tooling purged.

Wave X absurd sandbox: prepend a single `0|1` token from sha256-parity of the top-1 Jaccard curated chunk. Ablate vs full top-k RAG text prepend and bare H-EARLY on prog@128. Teachers score the **bare** task prompt.

Frozen: ε=0.05; k=2 RAG; win=256; max_chunks=1105 (257 available); seeds=3; max_new=32; identity + ≥RAG−ε clauses.

**Decision: KILL (code_lp -16.4182 < parent−ε -16.3192)**

## Arms

| arm | mean story_lp | mean code_lp | mean wall_ms | mean hit | mean ctx_len | n |
|-----|---------------|--------------|--------------|----------|--------------|---|
| H-EARLY bare | -14.8854 | -16.2692 | 22 | 0.000 | 699 | 12 |
| H-RAG full | -14.7418 | -16.9977 | 11 | 0.151 | 1214 | 12 |
| H-ABS-ORACLE1 | -14.6734 | -16.4182 | 9 | 0.151 | 701 | 12 |

## Lesson

1-bit marker **held story** and beat full RAG on `code_lp` (Δ ≈ +0.58 vs RAG) with tiny ctx, but still slipped below EARLY−ε on code (Δ ≈ −0.15). A hash side channel is not a free dual-gate substitute for bare EARLY (nor a RAG revive). Next E.1: **H-ABS-DNA** (3-mer codon packs) — not another RAG/oracle prepend.

Commands (purged): were `npm run nano:oracle1` / `nano:formal:horacle1*`.
