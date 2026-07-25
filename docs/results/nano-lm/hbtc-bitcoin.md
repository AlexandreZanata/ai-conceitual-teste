# H-BTC smoke — PACK tip gate on bitcoin domain

Wave W domain capacity: **bitcoin** prompts from curated Bitcoin Core README/developer-notes (MIT) + BIP-0001 / BIP-0032 (MIT, BSD-2-Clause), disjoint from harness/fit/ood/howto/prog. Teacher remains TinyStories. Kill if H-PACK loses its dual gate vs H-EARLY on this domain. No ood_long claim.
Mode: `BTC: PACK tip gate on bitcoin domain @128`; pack=`{'name': 'btc', 'n_prompts': 4, 'target_tokens': 128, 'source': '/home/iiii/PESSOAL-PROJETOS-ALEXANDRE/ai-conceitual-teste/nano_lm/prompts/btc_prompts.yaml'}`; cpu_threads=`14`; H-PACK=`PROMOTE (SERVE=min-wall + SROUTE=Pareto packs vs EARLY)`.

**Decision: PROMOTE (PACK tip gate holds on btc domain)**

## H-PACK on btc @128

| family | mean teacher_lp | Δ lp | mean tok/s | Δ tok/s | mean wall_ms | Δ wall | mean est GFLOPs | n |
|--------|-----------------|------|------------|---------|--------------|--------|-----------------|---|
| H-EARLY | -10.0831 | — | 658.0 | — | 15 | — | 6.278 | 3 |
| H-SERVE | -10.0843 | -0.0012 | 2385.5 | +1727.4 | 3 | -12 | 6.278 | 3 |
| H-SROUTE | -8.9749 | +1.1082 | 2957.1 | +2299.1 | 11 | -4 | 39.818 | 3 |

Tips unchanged. Wave W bitcoin domain probe.

Commands: `npm run nano:btc` → `npm run nano:btc:report`.
