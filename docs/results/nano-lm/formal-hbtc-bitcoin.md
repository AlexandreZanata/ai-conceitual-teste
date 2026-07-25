# Formal H-BTC — PACK tip gate on bitcoin domain

Source: `results/nano-lm/formal-hbtc/formal.json`
Wall clock: 16.8s

Wave W domain capacity: **bitcoin** prompts from curated Bitcoin Core README/developer-notes (MIT) + BIP-0001 / BIP-0032 (MIT, BSD-2-Clause), disjoint from harness/fit/ood/howto/prog. Teacher remains TinyStories. Kill if H-PACK loses its dual gate vs H-EARLY on this domain. No ood_long claim.
Mode: `BTC: PACK tip gate on bitcoin domain @128`; pack=`{'name': 'btc', 'n_prompts': 4, 'target_tokens': 128, 'source': '/home/iiii/PESSOAL-PROJETOS-ALEXANDRE/ai-conceitual-teste/nano_lm/prompts/btc_prompts.yaml'}`; cpu_threads=`14`; H-PACK=`PROMOTE (SERVE=min-wall + SROUTE=Pareto packs vs EARLY)`.

**Decision: PROMOTE (PACK tip gate holds on btc domain)**

## H-PACK on btc @128

| family | mean teacher_lp | Δ lp | mean tok/s | Δ tok/s | mean wall_ms | Δ wall | mean est GFLOPs | n |
|--------|-----------------|------|------------|---------|--------------|--------|-----------------|---|
| H-EARLY | -10.9223 | — | 637.0 | — | 17 | — | 7.591 | 3 |
| H-SERVE | -10.9160 | +0.0063 | 2359.5 | +1722.5 | 7 | -11 | 18.576 | 3 |
| H-SROUTE | -10.2692 | +0.6531 | 2868.1 | +2231.1 | 12 | -5 | 41.958 | 3 |

Tips unchanged. Wave W bitcoin domain probe.

Commands: `npm run nano:formal:hbtc` → `npm run nano:formal:hbtc:report`.
