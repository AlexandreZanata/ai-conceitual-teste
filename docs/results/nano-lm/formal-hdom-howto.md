# Formal H-DOM — PACK tip gate on howto domain

Source: `results/nano-lm/formal-hdom/formal.json`
Wall clock: 16.4s

New short domain capacity (Wave V): procedural **howto** prompts, disjoint from harness/fit/ood. Teacher remains TinyStories. Kill if H-PACK loses its dual gate vs H-EARLY on this domain.
Mode: `DOM: PACK tip gate on howto domain @128`; pack=`{'name': 'howto', 'n_prompts': 4, 'target_tokens': 128, 'source': '/home/iiii/PESSOAL-PROJETOS-ALEXANDRE/ai-conceitual-teste/nano_lm/prompts/dom_prompts.yaml'}`; cpu_threads=`12`; H-PACK=`PROMOTE (SERVE=min-wall + SROUTE=Pareto packs vs EARLY)`.

**Decision: PROMOTE (PACK tip gate holds on howto domain)**

## H-PACK on howto @128

| family | mean teacher_lp | Δ lp | mean tok/s | Δ tok/s | mean wall_ms | Δ wall | mean est GFLOPs | n |
|--------|-----------------|------|------------|---------|--------------|--------|-----------------|---|
| H-EARLY | -10.3649 | — | 609.4 | — | 18 | — | 7.644 | 3 |
| H-SERVE | -10.3673 | -0.0024 | 1170.7 | +561.4 | 7 | -11 | 7.644 | 3 |
| H-SROUTE | -9.2455 | +1.1194 | 2623.5 | +2014.1 | 13 | -5 | 42.212 | 3 |

Tips unchanged. Wave V domain capacity probe.

Commands: `npm run nano:formal:hdom` → `npm run nano:formal:hdom:report`.
