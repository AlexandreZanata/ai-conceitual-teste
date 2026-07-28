# H-FASTBE (BE3) — prod p50/p99 + anti-FP hold (**DONE** — PROMOTE)

> Lab: `.local/pesquisa.md` §4 · §9 BE3 · Session: `.local/wave-be/SESSION.md`  
> Parent: [formal-hshipuse-shipuse.md](formal-hshipuse-shipuse.md) · BE0 speed baseline (= H-FASTGAIN)  
> Module: `nano_lm/src/fastbe_ops.py` · Runner: `npm run nano:fastbe`  
> **Not** BD [formal-hfastgain-fastgain.md](formal-hfastgain-fastgain.md) (`npm run nano:bd:fastgain`) · **Not** AH [formal-hfastlift-fastlift.md](formal-hfastlift-fastlift.md) (`npm run nano:fastlift`) · **Not** BC [formal-hfastlift-bc2.md](formal-hfastlift-bc2.md) (`npm run nano:bc:fastlift`) · **Not** BB [formal-hfasthold-fasthold.md](formal-hfasthold-fasthold.md) (`npm run nano:bb:fasthold`)

## Hypothesis

Hold/improve prod-ask p50/p99 for LOOKUP·PEAK·DECODE·ABSTAIN; PROMOTE only if §1 anti-FP holds (BE-FOREVER FH 0 · BA…BD forever hold · AZ hold · over-refuse 0 · live FP 0) and live p99 does not regress vs BE0/H-FASTGAIN baseline — never warm-cache vanity; LOOKUP wall=0 ≠ speed IQ; sub-ms PEAK walls ≠ speed IQ; ≠ BD H-FASTGAIN archive · ≠ BC/AH H-FASTLIFT · ≠ BB H-FASTHOLD · ≠ BA H-FASTREAL · ≠ FP-for-ms

## Gate

| Metric | Result | Bar |
|--------|-------:|-----|
| be_forever_false_hit | **0** (12/12) | **0** |
| bd_forever_false_hit | **0** (12/12) | **0** |
| ba_forever_false_hit | **0** (15/15) | **0** |
| bb_forever_false_hit | **0** (15/15) | **0** |
| bc_forever_false_hit | **0** (18/18) | **0** |
| az_hold_false_hit | **0** (12/12) | **0** |
| overrefuse_miss | **0** (3/3) | **0** |
| live_fp | **0** | **0** |
| p99_regress | **False** ([]) | false (≤1.5× H-FASTGAIN) |
| modes_visible | **ABSTAIN · DECODE · LOOKUP · PEAK** (4/4) | 4/4 |
| Decision | **PROMOTE** | — |

## Latency p50/p99 (prod ask path)

| Path | p50 wall_ms | p99 wall_ms | n |
|------|------------:|------------:|--:|
| LOOKUP | **0.0** | **0.0** | 64 |
| PEAK | **0.009324998245574534** | **0.015838620602153245** | 128 |
| DECODE | **10.75098400178831** | **11.185807651199866** | 12 |
| ABSTAIN | **93.31420949456515** | **126.17945601174145** | 32 |

Samples: LOOKUP=64 · PEAK=128 · DECODE=12 · ABSTAIN=32

## Finding

1. Prod-path tetrad measured under max safe CPU (`cpus-6`, workers≤6).  
2. LOOKUP wall=0 **and** sub-ms PEAK walls **not** sold as speed IQ (regress gate uses base p99 ≥1ms).  
3. Anti-FP hold: BD FH 0 · BA FH 0 · BB FH 0 · BC FH 0 · AZ hold · over-refuse 0 · live FP 0.  
4. Live product p99 (DECODE·ABSTAIN) checked vs BE0/H-FASTGAIN (max ratio 1.5).  
5. Warm-cache vanity forbidden.  
6. Wall clock ~10.7s · workers parallel antifp packs.  
7. AH `nano:fastlift` · BC `nano:bc:fastlift` · BB `nano:bb:fasthold` archives untouched.  
8. Generative claim still locked (H-NANOGEN15 defer-once stance).

## Reproduce

```bash
npm run nano:fastbe
npm run nano:compint
# ≠ BD archive: npm run nano:fastbe
```

## Artifacts

- Summary: `results/nano-lm/wave-be/fastbe_summary.json`  
- Contract: `nano_lm/tests/test_fastbe.py`

## Claims

| Allowed | Forbidden |
|---------|-----------|
| AF packaged stack + AQ product layer + AS trust path + ablated DECODE (snippet-prefix + gibberish-tail STRICT) — not unlabeled open chat LM · not TAC unlocked | Open chat / mini-AGI |
| Publish prod p50/p99 | LOOKUP wall=0 as speed IQ |
| Anti-FP hold required | Trade FP for ms |
| H-FASTGAIN baseline p99 | Warm-cache vanity as product win |
| BD/AH/BC/BB FAST archives stay | Rewrite BD formal-hfastgain-fastgain |

SAFE note: SAFE / ADVSAFE false-hit score ≠ answer quality; SAFE = no wrong gold only (anti-FP); pack FH 0 ≠ forever held-out generalization; type/coercion wrong-bank LOOKUP = false-hit (str→int→def add); BA…BD forever PASS with BE-FOREVER FP = PACK THEATER; exact-gold ABSTAIN = product miss; gold-substring / gibberish-tail / span-fallback ≠ generative PROMOTE  
Anti-FP: LOOKUP|PEAK|DECODE|ABSTAIN labeled; never LOOKUP-as-IQ; never peak-as-open-chat; SAFE≠quality; gold-substring≠gen; type/coercion LOOKUP = false-hit (BE-FOREVER str→int→add); exact-gold ABSTAIN = miss (a.clear()); BA-FOREVER pow·mod·max·sort·len FH must stay 0; BB-FOREVER min·xor·absdiff·and·or FH must stay 0; BC-FOREVER floordiv·neg·gcd·lshift·rshift·nand FH must stay 0; BD-FOREVER reverse≠f-string · mul≠add FH must stay 0; AZ hold div·sub·BIP FH must stay 0; BA…BD PASS with BE FP = PACK THEATER; truncate-to-span≠gen IQ; DECODE gibberish≠content_ok; eval path = prod ask path; generative bar = BE5 only under real new method; no NANOGEN15 = NANOGEN14+rename; no CTX/SMART/FAST clone; no invent Wave BF without lab-book reopen; prefer compositional gate over bank stuffing; prefer HOLD/defer over fake PROMOTE

Next: **BE4 H-CTXBE** — context content bars without FP regress.
