# H-FASTGAIN (BD2) — prod p50/p99 + anti-FP hold (**DONE** — PROMOTE)

> Lab: `.local/pesquisa.md` §3 · §9 BD2 · Session: `.local/wave-bd/SESSION.md`  
> Parent: [formal-hsemint-semint.md](formal-hsemint-semint.md) · BD0 speed baseline (= H-FASTLIFT)  
> Module: `nano_lm/src/bd_fastgain_ops.py` · Runner: `npm run nano:bd:fastgain`  
> **Not** AH [formal-hfastlift-fastlift.md](formal-hfastlift-fastlift.md) (`npm run nano:fastlift`) · **Not** BC [formal-hfastlift-bc2.md](formal-hfastlift-bc2.md) (`npm run nano:bc:fastlift`) · **Not** BB [formal-hfasthold-fasthold.md](formal-hfasthold-fasthold.md) (`npm run nano:bb:fasthold`)

## Hypothesis

Hold/improve prod-ask p50/p99 for LOOKUP·PEAK·DECODE·ABSTAIN; PROMOTE only if §1 anti-FP holds (BD-FOREVER FH 0 · BA/BB/BC forever hold · AZ hold · over-refuse 0 · live FP 0) and live p99 does not regress vs BD0/H-FASTLIFT baseline — never warm-cache vanity; LOOKUP wall=0 ≠ speed IQ; sub-ms PEAK walls ≠ speed IQ; ≠ AH H-FASTLIFT archive · ≠ BC H-FASTLIFT rename · ≠ BB H-FASTHOLD archive · ≠ BA H-FASTREAL archive · ≠ FP-for-ms

## Gate

| Metric | Result | Bar |
|--------|-------:|-----|
| bd_forever_false_hit | **0** (12/12) | **0** |
| ba_forever_false_hit | **0** (15/15) | **0** |
| bb_forever_false_hit | **0** (15/15) | **0** |
| bc_forever_false_hit | **0** (18/18) | **0** |
| az_hold_false_hit | **0** (12/12) | **0** |
| overrefuse_miss | **0** (3/3) | **0** |
| live_fp | **0** | **0** |
| p99_regress | **False** ([]) | false (≤1.5× H-FASTLIFT) |
| modes_visible | **ABSTAIN · DECODE · LOOKUP · PEAK** (4/4) | 4/4 |
| Decision | **PROMOTE** | — |

## Latency p50/p99 (prod ask path)

| Path | p50 wall_ms | p99 wall_ms | n |
|------|------------:|------------:|--:|
| LOOKUP | **0.0** | **0.0** | 64 |
| PEAK | **0.009622501238482073** | **0.0291081194154686** | 128 |
| DECODE | **10.909949502092786** | **13.754690963978646** | 12 |
| ABSTAIN | **90.72191749874037** | **119.30380412799425** | 32 |

Samples: LOOKUP=64 · PEAK=128 · DECODE=12 · ABSTAIN=32

## Finding

1. Prod-path tetrad measured under max safe CPU (`cpus-4`, workers≤8).  
2. LOOKUP wall=0 **and** sub-ms PEAK walls **not** sold as speed IQ (regress gate uses base p99 ≥1ms).  
3. Anti-FP hold: BD FH 0 · BA FH 0 · BB FH 0 · BC FH 0 · AZ hold · over-refuse 0 · live FP 0.  
4. Live product p99 (DECODE·ABSTAIN) checked vs BD0/H-FASTLIFT (max ratio 1.5).  
5. Warm-cache vanity forbidden.  
6. Wall clock ~10.5s · workers parallel antifp packs.  
7. AH `nano:fastlift` · BC `nano:bc:fastlift` · BB `nano:bb:fasthold` archives untouched.  
8. Generative claim still locked (H-NANOGEN14 defer stance).

## Reproduce

```bash
npm run nano:bd:fastgain
npm run nano:semint
# ≠ AH archive: npm run nano:fastlift
# ≠ BC archive: npm run nano:bc:fastlift
```

## Artifacts

- Summary: `results/nano-lm/wave-bd/bd_fastgain_summary.json`  
- Contract: `nano_lm/tests/test_bd_fastgain.py`

## Claims

| Allowed | Forbidden |
|---------|-----------|
| AF packaged stack + AQ product layer + AS trust path + ablated DECODE (snippet-prefix + gibberish-tail STRICT) — not unlabeled open chat LM · not TAC unlocked | Open chat / mini-AGI |
| Publish prod p50/p99 | LOOKUP wall=0 as speed IQ |
| Anti-FP hold required | Trade FP for ms |
| H-FASTLIFT baseline p99 | Warm-cache vanity as product win |
| AH/BC/BB FAST archives stay | Rewrite AH formal-hfastlift-fastlift |

SAFE note: SAFE / ADVSAFE false-hit score ≠ answer quality; SAFE = no wrong gold only (anti-FP); pack FH 0 ≠ forever held-out generalization; semantic wrong-bank LOOKUP = false-hit (reverse→f-string · mul→add); BA+BB+BC forever PASS with BD-FOREVER FP = PACK THEATER; exact-gold ABSTAIN = product miss; gold-substring / gibberish-tail / span-fallback ≠ generative PROMOTE  
Anti-FP: LOOKUP|PEAK|DECODE|ABSTAIN labeled; never LOOKUP-as-IQ; never peak-as-open-chat; SAFE≠quality; gold-substring≠gen; semantic wrong-bank LOOKUP = false-hit (BD-FOREVER reverse→f-string / mul→add); exact-gold ABSTAIN = miss (a.clear()); BA-FOREVER pow·mod·max·sort·len FH must stay 0; BB-FOREVER min·xor·absdiff·and·or FH must stay 0; BC-FOREVER floordiv·neg·gcd·lshift·rshift·nand FH must stay 0; AZ hold div·sub·BIP FH must stay 0; BA+BB+BC PASS with BD FP = PACK THEATER; truncate-to-span≠gen IQ; DECODE gibberish≠content_ok; eval path = prod ask path; generative bar = BD4 only under real new method; no NANOGEN14 = NANOGEN13+rename; no CTX/SMART/FAST clone; no invent Wave BE without lab-book reopen; prefer HOLD/defer over fake PROMOTE

Next: **BD3 H-CTXGAIN** — context content bars without FP regress.
