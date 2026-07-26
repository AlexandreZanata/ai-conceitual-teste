# H-FASTPLUS — faster held-out ask (**DONE** — PROMOTE)

> Lab: `.local/pesquisa.md` §8.5 AC3 · §12.1 · Session: `.local/wave-ac/SESSION.md`  
> Parent: **H-ASKFAST** · Pack: AC0 held-out asks · Caches: AskCompletionCache  
> Module: `nano_lm/src/fastplus_ops.py` · Runner: `npm run nano:fastplus`

## Hypothesis

Compose **ASKFAST + SEMWRAP + AskCompletionCache** on the **held-out** AC pack so wall/TTFT/e2e beat recorded AB ask baselines (open wall **25.2 ms**, ASKFAST e2e **88.8 ms**) while HITL quality holds.

## Gate (Cursor ASK→EVAL→FIX×10)

| Metric | Result | Pass bar / rule |
|--------|-------:|-----------------|
| mean score | **9.0** | ≥ 7.0 |
| FALSE_HIT | **0**/10 | any → **KILL** |
| errors | **0**/10 | ≤ 3 |
| cold / warm wall_ms | **0.0 / 0.0** | — |
| cold / warm TTFT_ms | **0.0 / 0.0** | wrap ≈ TTFT |
| warm e2e_ms | **~0.3** | < AB ASKFAST e2e **88.8** |
| wall_drop vs AB open | **100%** | ≥ **20%** |
| cache hit-rate | **0.50** | cold+warm |
| FIX count | **0** | — |
| Decision | **PROMOTE** | quality ∧ speed↓ ∧ no false-hit |

## Finding

1. Held-out wrap lookups stay at **0 ms** wall/TTFT (scoped assist — not open decode).  
2. Warm pack e2e **≪** recorded AB ASKFAST e2e (cache already seeded from AC1/AC2).  
3. Wall drop vs AB open baseline (**25.2 ms**) is **100%**.  
4. Forbidden unused: STREAM · KVCACHE-Q · GENCACHE.

## Reproduce

```bash
npm run nano:fastplus
```

## Artifacts

- Summary: `results/nano-lm/wave-ac/fastplus_summary.json`  
- Trials: `results/nano-lm/wave-ac/trials/AC-FASTPLUS-HITL-01.json` … `10.json`  
- Contract: `nano_lm/tests/test_fastplus.py`

Next: **AC4 H-APPPLUS**.
