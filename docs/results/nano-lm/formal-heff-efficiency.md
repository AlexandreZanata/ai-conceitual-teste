# Formal H-EFF — PACK efficiency on prog+btc vs Phase B

Source: `results/nano-lm/formal-heff/formal.json`
Wall clock: 33.1s

Wave W efficiency: re-measure **H-PACK** SERVE wall/tok/s/GFLOPs on programming + bitcoin packs @128 vs Phase B formal baselines. PROMOTE iff any domain is at quality floor (SERVE ≥ EARLY−ε) **and** wall↓ or tok/s↑ vs Phase B; else **HOLD**. No new genes. TPACK/AMORT remain story-train-only.
Mode: `EFF formal: PACK re-measure prog+btc @128 vs Phase B SERVE; fit≠eval genes`; cpu_threads=`14`; packs=`{'prog': {'name': 'prog', 'n_prompts': 4, 'target_tokens': 128, 'source': '/home/iiii/PESSOAL-PROJETOS-ALEXANDRE/ai-conceitual-teste/nano_lm/prompts/prog_prompts.yaml'}, 'btc': {'name': 'btc', 'n_prompts': 4, 'target_tokens': 128, 'source': '/home/iiii/PESSOAL-PROJETOS-ALEXANDRE/ai-conceitual-teste/nano_lm/prompts/btc_prompts.yaml'}}`.

**Decision: PROMOTE (PACK efficiency ↑ at quality floor on prog,btc)**

### prog

| arm | mean teacher_lp | mean tok/s | mean wall_ms | mean GFLOPs |
|-----|-----------------|------------|--------------|-------------|
| H-EARLY | -8.1626 | 652.9 | 17 | 7.859 |
| H-SERVE | -8.1653 | 2523.0 | 3 | 7.859 |

Phase B SERVE baseline: lp=-8.1653, tok/s=1956.9, wall_ms=4.

### btc

| arm | mean teacher_lp | mean tok/s | mean wall_ms | mean GFLOPs |
|-----|-----------------|------------|--------------|-------------|
| H-EARLY | -10.9223 | 756.9 | 10 | 7.591 |
| H-SERVE | -10.9160 | 2836.5 | 6 | 18.576 |

Phase B SERVE baseline: lp=-10.9160, tok/s=2359.5, wall_ms=7.


Commands: `npm run nano:formal:heff` → `npm run nano:formal:heff:report`.
