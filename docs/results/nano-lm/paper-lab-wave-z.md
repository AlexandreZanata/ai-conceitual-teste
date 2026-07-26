# Paper-lab — Wave Z HITL (≤5M student)

> Companion to [wave-z-hitl.md](wave-z-hitl.md). English lab note for external readers.

## Question

Do Wave X+/Y **PFB / QT / PACK** recipe wins imply a usable **interactive** nano LM (≤5M) under the lab ask path?

## Answer

**No.** Formal dual-gate and teacher LP are necessary but not sufficient for product Q&A.

| Arm / stage | Observation |
|-------------|-------------|
| Z1 raw ask | Period-token collapse (mean 1.0) |
| Z2 / Z4 wrap | Error-bank **WRAP_LOOKUP** recovers HITL (mean 9.0) |
| Z3 H-ZERR | Story floor held; open decode still fails (Z4C) |
| Product | **H-ZWRAP** known-ask demo; not open chat |

## Takeaway one-liner

**PFB recipes ≠ interactive LM; wrap + error-bank loop.**

## Cite

- [wave-z-hitl.md](wave-z-hitl.md) · [wave-z-hitl-z4.md](wave-z-hitl-z4.md) · [wave-z-depl-y.md](wave-z-depl-y.md)  
- Recipes: [RECIPES.md](RECIPES.md) · Card: [champion-card.md](champion-card.md)
