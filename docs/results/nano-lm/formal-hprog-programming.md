# Formal H-PROG — PACK tip gate on programming domain

Source: `results/nano-lm/formal-hprog/formal.json`
Wall clock: 16.1s

Wave W domain capacity: **programming** prompts from curated Python tutorial (PSF) + Rust book variables chapter (PSF, CC-BY-SA / MIT Apache-2.0), disjoint from harness/fit/ood/howto. Teacher remains TinyStories. Kill if H-PACK loses its dual gate vs H-EARLY on this domain. No ood_long claim.
Mode: `PROG: PACK tip gate on programming domain @128`; pack=`{'name': 'prog', 'n_prompts': 4, 'target_tokens': 128, 'source': '/home/iiii/PESSOAL-PROJETOS-ALEXANDRE/ai-conceitual-teste/nano_lm/prompts/prog_prompts.yaml'}`; cpu_threads=`14`; H-PACK=`PROMOTE (SERVE=min-wall + SROUTE=Pareto packs vs EARLY)`.

**Decision: PROMOTE (PACK tip gate holds on prog domain)**

## H-PACK on prog @128

| family | mean teacher_lp | Δ lp | mean tok/s | Δ tok/s | mean wall_ms | Δ wall | mean est GFLOPs | n |
|--------|-----------------|------|------------|---------|--------------|--------|-----------------|---|
| H-EARLY | -8.1626 | — | 631.6 | — | 18 | — | 7.859 | 3 |
| H-SERVE | -8.1653 | -0.0027 | 1956.9 | +1325.3 | 4 | -13 | 7.859 | 3 |
| H-SROUTE | -7.0635 | +1.0991 | 2958.8 | +2327.2 | 12 | -6 | 43.230 | 3 |

Tips unchanged. Wave W programming domain probe.

Commands: `npm run nano:formal:hprog` → `npm run nano:formal:hprog:report`.
