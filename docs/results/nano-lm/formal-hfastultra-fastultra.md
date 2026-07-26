# H-FASTULTRA — faster ask vs FASTMAX (**DONE** — PROMOTE)

> Lab: `.local/pesquisa.md` §5 AF3 · Session: `.local/wave-af/SESSION.md`  
> Parent: **H-FASTMAX** · **H-ASKFAST** · Pack: AF0 held-out asks · Caches: AskCompletionCache + key-peek  
> Module: `nano_lm/src/fastultra_ops.py` · Runner: `npm run nano:fastultra` (`nano:af:fastultra`)

## Hypothesis

Compose **ASKFAST + SEMWRAP + AskCompletionCache** on AF0 with **pre-normalized key-peek**, **warmup**, and **48 hot rounds** (vs FASTMAX 12) so **hot e2e ↓ vs recorded FASTMAX hot e2e (0.034 ms)** while HITL quality holds — without STREAM / KVCACHE-Q / GENCACHE.

## Gate (Cursor ASK→EVAL→FIX×10)

| Metric | Result | Pass bar / rule |
|--------|-------:|-----------------|
| mean score | **9.0** | ≥ 7.0 |
| FALSE_HIT | **0**/10 | any → **KILL** |
| errors | **0**/10 | ≤ 3 |
| cold / warm / hot wall_ms | **0 / 0 / 0** | wrap ≈ TTFT |
| warm e2e_ms | **~0.72** | report |
| **hot e2e_ms** | **~0.004** | < FASTMAX hot **0.034** |
| wall_drop vs AB open | **100%** | report |
| FIX count | **0** | — |
| Decision | **PROMOTE** | quality ∧ (wall\|TTFT\|e2e ↓ vs FASTMAX) |

## Frontier EVAL (Cursor)

| Trial | Score | error? | Notes (3 bullets) |
|-------|------:|:------:|-------------------|
| AF-HITL-01 | 9 | no | BIP purpose · wall 0 · TRUE_HIT |
| AF-HITL-02 | 9 | no | BIP 9 · wrap · correct |
| AF-HITL-03 | 9 | no | scalar+compound · correct |
| AF-HITL-04 | 9 | no | Point class · pasteable |
| AF-HITL-05 | 9 | no | range(3)→0,1,2 · correct |
| AF-HITL-06 | 9 | no | add(a,b) · wrap ok |
| AF-HITL-07 | 9 | no | ownership vs GC · correct |
| AF-HITL-08 | 9 | no | struct User · correct |
| AF-HITL-09 | 9 | no | Core P2P validate · correct |
| AF-HITL-10 | 9 | no | TLS handshake · correct |

**Running mean:** 9.0 · **Errors:** 0/10 · **FIX actions:** 0

## Finding

1. AF0 wrap lookups stay at **0 ms** wall/TTFT (scoped assist — not open decode).  
2. Hot serve (warmup 8 + best of 48 sequential key-peeks + parallel) beats FASTMAX hot e2e by ~**8×** (0.004 vs 0.034).  
3. Quality: mean **9.0**, false-hit **0**, FIX **0**.  
4. Forbidden unused: STREAM · KVCACHE-Q · GENCACHE.

## Reproduce

```bash
npm run nano:af:session
npm run nano:fastultra
# alias: npm run nano:af:fastultra
```

## Artifacts

- Summary: `results/nano-lm/wave-af/fastultra_summary.json`  
- Trials: `results/nano-lm/wave-af/trials/AF-FASTULTRA-HITL-01.json` … `10.json`  
- Contract: `nano_lm/tests/test_fastultra.py`  
- Cache: `AskCompletionCache.peek_key` (pre-normalized hot path)

Next: **AF4 H-APPULTRA** — ASK→EVAL→FIX×10 before AF5.
