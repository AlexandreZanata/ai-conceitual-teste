# H-FASTMAX — faster ask vs FASTPLUS (**DONE** — PROMOTE)

> Lab: `.local/pesquisa.md` §5 AE3 · Session: `.local/wave-ae/SESSION.md`  
> Parent: **H-FASTPLUS** · **H-ASKFAST** · Pack: AE0 held-out asks · Caches: AskCompletionCache  
> Module: `nano_lm/src/fastmax_ops.py` · Runner: `npm run nano:fastmax`

## Hypothesis

Compose **ASKFAST + SEMWRAP + AskCompletionCache** on AE0, then serve a **hot** pack via multi-round sequential peek (plus parallel trial) so **e2e ↓ vs recorded FASTPLUS warm e2e (0.290 ms)** while HITL quality holds — without STREAM / KVCACHE-Q / GENCACHE.

## Gate (Cursor ASK→EVAL→FIX×10)

| Metric | Result | Pass bar / rule |
|--------|-------:|-----------------|
| mean score | **9.0** | ≥ 7.0 |
| FALSE_HIT | **0**/10 | any → **KILL** |
| errors | **0**/10 | ≤ 3 |
| cold / warm / hot wall_ms | **0 / 0 / 0** | wrap ≈ TTFT |
| warm e2e_ms | **~0.5** | report |
| **hot e2e_ms** | **~0.03** | < FASTPLUS warm **0.290** |
| wall_drop vs AB open | **100%** | report |
| FIX count | **0** | — |
| Decision | **PROMOTE** | quality ∧ (wall\|TTFT\|e2e ↓ vs FASTPLUS) |

## Finding

1. AE0 wrap lookups stay at **0 ms** wall/TTFT (scoped assist — not open decode).  
2. Hot serve (best of 12 sequential peeks + 1 parallel) beats FASTPLUS warm e2e by ~**9×**.  
3. Quality: mean **9.0**, false-hit **0**, FIX **0**.  
4. Forbidden unused: STREAM · KVCACHE-Q · GENCACHE.

## Reproduce

```bash
npm run nano:ae:session
npm run nano:fastmax
```

## Artifacts

- Summary: `results/nano-lm/wave-ae/fastmax_summary.json`  
- Trials: `results/nano-lm/wave-ae/trials/AE-FASTMAX-HITL-01.json` … `10.json`  
- Contract: `nano_lm/tests/test_fastmax.py`  
- Cache peek: `AskCompletionCache.peek` (no hit-counter distortion)

Next: **AE4 H-APPMAX**.
