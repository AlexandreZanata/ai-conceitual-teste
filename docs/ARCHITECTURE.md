# Architecture — nano generative LM (active)

> EvoGen C++ PoC docs: [`archive/evogen/`](archive/evogen/README.md).

## Active stack

| Layer | Location | Role |
|-------|----------|------|
| Student ≤5M | `nano_lm/` | Causal LM train / decode / recipes |
| Teacher | TinyStories-33M (HF) | Log-prob judge (story harness) |
| Tips | STAG′ / EARLY / POOL | Train + decode champions |
| Recipes | PACK / TPACK+AMORT / QPACK | Speed / steps / in-harness quality |
| Curated KB | `nano_lm/data/curated/` | Programming + frontier public corpora |
| Lab book | `.local/pesquisa.md` | Wave queue (gitignored) |

## Frozen (not active)

C++ binary `evogen`, survival arena, A/B/C TB benches — archived scientifically; code retained for reproducibility only.
