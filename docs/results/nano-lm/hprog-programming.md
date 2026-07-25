# H-PROG smoke — PACK tip gate on programming domain

Wave W domain capacity: **programming** prompts from curated Python tutorial (PSF) + Rust book variables chapter (PSF, CC-BY-SA / MIT Apache-2.0), disjoint from harness/fit/ood/howto. Teacher remains TinyStories. Kill if H-PACK loses its dual gate vs H-EARLY on this domain. No ood_long claim.
Mode: `PROG: PACK tip gate on programming domain @128`; pack=`{'name': 'prog', 'n_prompts': 4, 'target_tokens': 128, 'source': '/home/iiii/PESSOAL-PROJETOS-ALEXANDRE/ai-conceitual-teste/nano_lm/prompts/prog_prompts.yaml'}`; cpu_threads=`14`; H-PACK=`PROMOTE (SERVE=min-wall + SROUTE=Pareto packs vs EARLY)`.

**Decision: PROMOTE (PACK tip gate holds on prog domain)**

## H-PACK on prog @128

| family | mean teacher_lp | Δ lp | mean tok/s | Δ tok/s | mean wall_ms | Δ wall | mean est GFLOPs | n |
|--------|-----------------|------|------------|---------|--------------|--------|-----------------|---|
| H-EARLY | -10.1603 | — | 639.8 | — | 16 | — | 6.501 | 3 |
| H-SERVE | -10.1613 | -0.0010 | 2276.9 | +1637.1 | 3 | -12 | 6.501 | 3 |
| H-SROUTE | -8.4523 | +1.7080 | 2405.1 | +1765.3 | 12 | -3 | 41.018 | 3 |

Tips unchanged. Wave W programming domain probe.

Commands: `npm run nano:prog` → `npm run nano:prog:report`.
