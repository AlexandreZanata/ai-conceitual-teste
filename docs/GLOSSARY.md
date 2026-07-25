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
| **PROMOTE / KILL** | Smoke+formal decision vs parent tip/recipe |

Never call evolutionary individuals “coding agents.”
