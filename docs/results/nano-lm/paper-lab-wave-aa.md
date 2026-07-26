# Paper-lab — Wave AA (post-freeze product expansion)

> Companion to [wave-aa-summary.md](wave-aa-summary.md). English lab note for external readers.

## Question

After Wave Z proved **PFB ≠ interactive LM**, can honest product expansion (bank growth, paraphrase stress, open-decode align, preference retrain, doc sync) make the ≤5M student a usable open chat LM?

## Answer

**No.** Expansion strengthens the **known-ask wrap** demo and maps failure modes; it does not unlock open chat.

| Stage | Observation |
|-------|-------------|
| H-WRAPBANK | Exact LOOKUP golds grow (HITL mean 9.0) |
| H-PARA | Paraphrases miss LOOKUP (0 false-hits) — brittleness |
| H-SERVEALIGN | QPFB2+BEAMKV beats Z1 periods; still fails product HITL bar |
| H-ZPREF | Preference gold≻raw KILLs on story parent−ε |
| H-DEPL-DOC | One-pagers stay aligned with DEPL-Y |

## Takeaway one-liner

**Known-ask product = H-ZWRAP + H-WRAPBANK; not open chat.**

## Cite

- [wave-aa-summary.md](wave-aa-summary.md) · [wave-z-hitl.md](wave-z-hitl.md) · [wave-z-depl-y.md](wave-z-depl-y.md)  
- Formals: WRAPBANK · PARA · SERVEALIGN · ZPREF · DEPL-DOC  
- Recipes: [RECIPES.md](RECIPES.md) · Card: [champion-card.md](champion-card.md)
