# Glossary — nano generative LM (active)

> Full EvoGen survival terms: [`archive/evogen/GLOSSARY.md`](archive/evogen/GLOSSARY.md).

| Term | Meaning |
|------|---------|
| **Student** | ≤5M param causal LM under study (not a “coding agent”) |
| **Teacher** | Frozen larger LM scoring completions (TinyStories-33M on story harness) |
| **Code teacher** | Frozen tiny public code LM scoring prog/btc completions (`code_teacher_lp`; H-TCHR: `bigcode/tiny_starcoder_py`) |
| **Story teacher** | TinyStories-33M; never silently swapped with the code teacher |
| **Tip** | Official champion decode/train config (STAG′, EARLY, POOL) |
| **Recipe** | Deployable pack (PACK serve-fast, TPACK+AMORT train, QPACK quality) |
| **Domain pack** | Held-out prompt set (howto, code, bitcoin, …) for capacity/transfer |
| **Curated KB** | Public official corpora under `nano_lm/data/curated/` |
| **Dual gate** | Quality (teacher_lp / domain metric) **and** wall/GFLOPs |
| **H-QT** | Int8 weight-only quantized student serve (Linear; skip tied lm_head) |
| **H-CKD** | Soft-KD from code teacher (smoke **KILL**; see archive) |
| **H-QCTX** | Born-rule amplitude attention @ long L (smoke **KILL**; see archive) |
| **H-QCOMP** | Classical-shadow KV sketch (smoke PROMOTE → formal **KILL**; see archive) |
| **H-Q-QUBITKV** | Critical KV + residual sketch (smoke **KILL**; see archive) |
| **H-GENC** | Genetic context/serve genome under BUD (smoke+formal **PROMOTE**) |
| **H-GENQ-ABS** | Amplitude/measurement genetics vs GENC (smoke+formal **KILL**; see archive) |
| **H-DIST** | Shared-vocab Neo KD on curated prog (smoke **KILL**; see archive) |
| **H-Q-SLOT** | K curated slots + measure commit (smoke **KILL**; see archive) |
| **H-Q-INTERF** | Dual-teacher α-BoN score interference (smoke **KILL**; see archive) |
| **H-ABS-REV** | Time-reversed KV prefill (smoke **KILL**; see archive) |
| **H-Q-ANNEAL** | Per-token T(t)/conf(t) cooling on EARLY (smoke **KILL**; see archive) |
| **H-ABS-SPIRAL** | Hilbert-curve absolute position remap (smoke **KILL**; see archive) |
| **H-Q-GROVER** | R-round next-token mass amplify p∝p² (smoke **KILL**; see archive) |
| **H-Q-TUNNEL** | Tiny ε leak past causal MASK (smoke **KILL**; identity vs EARLY; see archive) |
| **H-Q-BELL** | Distant (i,i+τ) K/V mean couple (smoke **KILL**; identity vs EARLY; see archive) |
| **H-ABS-ORACLE1** | 1-bit sha256 parity marker vs RAG prepend (smoke **KILL**; code↓ vs EARLY; see archive) |
| **H-ABS-DNA** | Codon-like 3-mer BPE packs (smoke **KILL**; story↓; see archive) |
| **H-ABS-DEBATE** | Dual early-exit halves + BoN commit (smoke **KILL**; identity; see archive) |
| **H-ABS-HOLO** | 4-bit KV + RFF holographic checksum (smoke **KILL**; code↓ vs EARLY−ε; see archive) |
| **H-ABS-PHASE** | 2D rotary / complex e^{iθ} on Q/K (smoke **KILL**; identity vs EARLY; see archive) |
| **H-Q-ENTPOS** | Low-rank bilinear pos⊗tok attn bias (smoke **KILL**; identity vs EARLY; see archive) |
| **H-Q-MEASURE** | Mid-decode RAG slot measure/commit (smoke **KILL**; code↓ vs EARLY−ε; see archive) |
| **H-Q-TELE** | Mid-layer residual RAG teleport (smoke **KILL**; identity vs EARLY; see archive) |
| **H-Q-WIGNER** | Signed top-k logit quasi-prob (Wave X next; `.local/pesquisa.md`) |
| **PROMOTE / KILL** | Smoke+formal decision vs parent tip/recipe |

Never call evolutionary individuals “coding agents.”
