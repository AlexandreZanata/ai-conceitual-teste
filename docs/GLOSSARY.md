# Glossary — nano generative LM (active)

> Full EvoGen survival terms: [`archive/evogen/GLOSSARY.md`](archive/evogen/GLOSSARY.md).

| Term | Meaning |
|------|---------|
| **Student** | ≤5M param causal LM under study (not a “coding agent”) |
| **Teacher** | Frozen larger LM scoring completions (TinyStories-33M on story harness) |
| **Tip** | Official champion decode/train config (STAG′, EARLY, POOL) |
| **Recipe** | Deployable pack (PACK serve-fast, TPACK+AMORT train, QPACK quality) |
| **Domain pack** | Held-out prompt set (howto, code, bitcoin, …) for capacity/transfer |
| **Curated KB** | Public official corpora under `nano_lm/data/curated/` |
| **Dual gate** | Quality (teacher_lp / domain metric) **and** wall/GFLOPs |
| **PROMOTE / KILL** | Smoke+formal decision vs parent tip/recipe |

Never call evolutionary individuals “coding agents.”
