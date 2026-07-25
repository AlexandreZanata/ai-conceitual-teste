# H-DOM smoke — PACK tip gate on howto domain

New short domain capacity (Wave V): procedural **howto** prompts, disjoint from harness/fit/ood. Teacher remains TinyStories. Kill if H-PACK loses its dual gate vs H-EARLY on this domain.
Mode: `DOM: PACK tip gate on howto domain @128`; pack=`{'name': 'howto', 'n_prompts': 4, 'target_tokens': 128, 'source': '/home/iiii/PESSOAL-PROJETOS-ALEXANDRE/ai-conceitual-teste/nano_lm/prompts/dom_prompts.yaml'}`; cpu_threads=`12`; H-PACK=`PROMOTE (SERVE=min-wall + SROUTE=Pareto packs vs EARLY)`.

**Decision: PROMOTE (PACK tip gate holds on howto domain)**

## H-PACK on howto @128

| family | mean teacher_lp | Δ lp | mean tok/s | Δ tok/s | mean wall_ms | Δ wall | mean est GFLOPs | n |
|--------|-----------------|------|------------|---------|--------------|--------|-----------------|---|
| H-EARLY | -9.7482 | — | 622.3 | — | 16 | — | 6.323 | 3 |
| H-SERVE | -9.7495 | -0.0014 | 1227.3 | +605.1 | 6 | -11 | 6.323 | 3 |
| H-SROUTE | -9.0273 | +0.7209 | 2302.2 | +1679.9 | 12 | -4 | 40.058 | 3 |

Tips unchanged. Wave V domain capacity probe.

Commands: `npm run nano:dom` → `npm run nano:dom:report`.
