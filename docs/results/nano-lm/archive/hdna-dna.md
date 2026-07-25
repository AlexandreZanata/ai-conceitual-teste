# H-ABS-DNA smoke — codon-like 3-mer BPE packs (**KILL**)

> Smoke **KILL**. Do not claim codon compression dual-gate win. Tooling purged.

Wave X absurd sandbox: pack every k=3 BPE ids into one hashed vocab “codon” for prefill, then generate BPE tokens normally (classical translate). Parent = bare H-EARLY on prog@128.

Frozen: k=3; ε=0.05; max_new=32; seeds=3; prog pack; bits/orig + compress audit.

**Decision: KILL (story_lp -15.6840 < parent−ε -14.9354)**

## Arms

| arm | mean story_lp | mean code_lp | mean wall_ms | mean compress | mean bits/orig | n |
|-----|---------------|--------------|--------------|---------------|----------------|---|
| H-EARLY bare | -14.8854 | -16.2692 | 22 | 1.000 | — | 12 |
| H-ABS-DNA k=3 | -15.6840 | -15.7925 | 8 | 0.336 | 5.24 | 12 |

## Lesson

Codon packing **compressed** prefill (~3×; bits/orig≈5.2) and nudged `code_lp` up with wall↓, but **broke** story dual gate (Δ ≈ −0.80 vs parent−ε). Hash-merged BPE codons are not a free PACK/EARLY upgrade. Next E.1: **H-ABS-DEBATE** (dual ≤2.5M halves) — not another codon/oracle/RAG compress.

Commands (purged): were `npm run nano:dna` / `nano:formal:hdna*`.
