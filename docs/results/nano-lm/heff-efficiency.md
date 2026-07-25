# H-EFF smoke — PACK efficiency on prog+btc vs Phase B

Wave W efficiency: re-measure **H-PACK** SERVE wall/tok/s/GFLOPs on programming + bitcoin packs @128 vs Phase B formal baselines. PROMOTE iff any domain is at quality floor (SERVE ≥ EARLY−ε) **and** wall↓ or tok/s↑ vs Phase B; else **HOLD**. No new genes. TPACK/AMORT remain story-train-only.
Mode: `EFF smoke: PACK re-measure prog+btc @128 vs Phase B SERVE; TPACK/AMORT remain story-train-only (unchanged)`; cpu_threads=`14`; packs=`{'prog': {'name': 'prog', 'n_prompts': 4, 'target_tokens': 128, 'source': '/home/iiii/PESSOAL-PROJETOS-ALEXANDRE/ai-conceitual-teste/nano_lm/prompts/prog_prompts.yaml'}, 'btc': {'name': 'btc', 'n_prompts': 4, 'target_tokens': 128, 'source': '/home/iiii/PESSOAL-PROJETOS-ALEXANDRE/ai-conceitual-teste/nano_lm/prompts/btc_prompts.yaml'}}`.

**Decision: PROMOTE (PACK efficiency ↑ at quality floor on prog,btc)**

### prog

| arm | mean teacher_lp | mean tok/s | mean wall_ms | mean GFLOPs |
|-----|-----------------|------------|--------------|-------------|
| H-EARLY | -10.1603 | 673.6 | 15 | 6.501 |
| H-SERVE | -10.1613 | 2503.3 | 3 | 6.501 |

Phase B SERVE baseline: lp=-8.1653, tok/s=1956.9, wall_ms=4.

### btc

| arm | mean teacher_lp | mean tok/s | mean wall_ms | mean GFLOPs |
|-----|-----------------|------------|--------------|-------------|
| H-EARLY | -10.0831 | 744.1 | 9 | 6.278 |
| H-SERVE | -10.0843 | 2719.6 | 2 | 6.278 |

Phase B SERVE baseline: lp=-10.9160, tok/s=2359.5, wall_ms=7.


Commands: `npm run nano:eff` → `npm run nano:eff:report`.
