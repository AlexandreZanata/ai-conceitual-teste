# Formal H-DECK2 vs H-DECK (top_k ablation, equal pop×gens)

Source: `results/nano-lm/formal-hdeck2/formal.json`
Wall clock: 111.8s

Shared B2 KD ckpts from formal H-DECK. pop=8 gens=12; top_k∈{1,2,3}.
Fit: `fit_prompts.yaml`. Eval: `eval_prompts.yaml`. Seeds: 0,1,2.
Kill if best k ≤ H-DECK (k=2).

| top_k / family | mean teacher_lp | Δ vs k=2 | mean wall_ms | n |
|----------------|-----------------|----------|--------------|---|
| B4 | -14.4943 | — | 78 | 3 |
| H-DECK2 k=1 | -11.7632 | +0.2490 | 240 | 3 |
| H-DECK2 k=2 | -12.0123 | — | 165 | 3 |
| H-DECK2 k=3 | -11.7777 | +0.2346 | 168 | 3 |

**Decision:** PROMOTE (best top_k=1 > H-DECK)

Best top_k: 1. B4 mean lp: -14.4943.

Commands: `npm run nano:formal:hdeck2` → `npm run nano:formal:hdeck2:report`.
