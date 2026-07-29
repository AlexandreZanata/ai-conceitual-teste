# H-FASTBF (BF3) — prod p50/p99 + anti-FP hold (**DONE** — PROMOTE)

> Lab: `.local/pesquisa.md` §4 · §9 BF3 · Session: `.local/wave-bf/SESSION.md`  
> Parent: [formal-hshipuse2-shipuse2.md](formal-hshipuse2-shipuse2.md) · BF0 speed baseline (= H-FASTBE)  
> Module: `nano_lm/src/fastbf_ops.py` · Runner: `npm run nano:fastbf`  
> **Not** BE [formal-hfastbe-fastbe.md](formal-hfastbe-fastbe.md) (`npm run nano:fastbe`) · **Not** BD [formal-hfastgain-fastgain.md](formal-hfastgain-fastgain.md) (`npm run nano:bd:fastgain`) · **Not** AH/BC/BB FAST archives

## Hypothesis

Hold/improve prod-ask p50/p99 for LOOKUP·PEAK·DECODE·ABSTAIN; PROMOTE only if §1 anti-FP holds (BF-FOREVER FH 0 · BA…BE forever hold · AZ hold · over-refuse 0 · live FP 0) and live p99 does not regress vs BF0/H-FASTBE baseline — never warm-cache vanity; LOOKUP wall=0 ≠ speed IQ; sub-ms PEAK walls ≠ speed IQ; ≠ BE H-FASTBE archive · ≠ BD H-FASTGAIN · ≠ BC/AH H-FASTLIFT · ≠ BB H-FASTHOLD · ≠ BA H-FASTREAL · ≠ FP-for-ms

## Gate

| Metric | Result | Bar |
|--------|-------:|-----|
| bf_forever_false_hit | **0** (12/12) | **0** |
| be_forever_false_hit | **0** (12/12) | **0** |
| bd_forever_false_hit | **0** (12/12) | **0** |
| ba_forever_false_hit | **0** (15/15) | **0** |
| bb_forever_false_hit | **0** (15/15) | **0** |
| bc_forever_false_hit | **0** (18/18) | **0** |
| az_hold_false_hit | **0** (12/12) | **0** |
| overrefuse_miss | **0** (3/3) | **0** |
| live_fp | **0** | **0** |
| p99_regress | **False** ([]) | false (≤1.5× H-FASTBE) |
| modes_visible | **ABSTAIN · DECODE · LOOKUP · PEAK** (4/4) | 4/4 |
| Decision | **PROMOTE** | — |

## Latency p50/p99 (prod ask path)

| Path | p50 wall_ms | p99 wall_ms | n |
|------|------------:|------------:|--:|
| LOOKUP | **0.0** | **0.0** | 64 |
| PEAK | **0.020638000023609493** | **0.028944830004320465** | 128 |
| DECODE | **10.507157999995798** | **10.882093060029092** | 12 |
| ABSTAIN | **87.36960300001329** | **110.29079292000351** | 32 |

Samples: LOOKUP=64 · PEAK=128 · DECODE=12 · ABSTAIN=32

## Finding

1. Prod-path tetrad measured under max safe CPU (`cpus-6`, workers≤6).  
2. LOOKUP wall=0 **and** sub-ms PEAK walls **not** sold as speed IQ.  
3. Anti-FP hold: BF FH 0 · BE…BA forever · AZ hold · over-refuse 0 · live FP 0.  
4. Live product p99 (DECODE·ABSTAIN) checked vs BF0/H-FASTBE (max ratio 1.5).  
5. Warm-cache vanity forbidden.  
6. Wall clock ~10.5s · workers parallel antifp packs.  
7. BE `nano:fastbe` · BD/AH/BC/BB FAST archives untouched.  
8. Generative claim still locked (gen stance SKIP; H-NANOGEN16 not opened).

## Reproduce

```bash
npm run nano:fastbf
npm run nano:predint
# ≠ BE archive: npm run nano:fastbe
```

## Artifacts

- Summary: `results/nano-lm/wave-bf/fastbf_summary.json`  
- Contract: `nano_lm/tests/test_fastbf.py`

## Claims

| Allowed | Forbidden |
|---------|-----------|
| AF packaged stack + AQ product layer + AS trust path + ablated DECODE (snippet-prefix + gibberish-tail STRICT) — not unlabeled open chat LM · not TAC unlocked | Open chat / mini-AGI |
| Publish prod p50/p99 | LOOKUP wall=0 as speed IQ |
| Anti-FP hold required | Trade FP for ms |
| H-FASTBE baseline p99 | Warm-cache vanity as product win |
| BE/BD/AH/BC/BB FAST archives stay | Rewrite BE formal-hfastbe-fastbe |

SAFE note: SAFE / ADVSAFE false-hit score ≠ answer quality; SAFE = no wrong gold only (anti-FP); pack FH 0 ≠ forever held-out generalization; predicate/boolean wrong-bank LOOKUP = false-hit (even→def add); BA…BE forever PASS with BF-FOREVER FP = PACK THEATER; exact-gold ABSTAIN = product miss; gold-substring / gibberish-tail / span-fallback ≠ generative PROMOTE  
Anti-FP: LOOKUP|PEAK|DECODE|ABSTAIN labeled; never LOOKUP-as-IQ; never peak-as-open-chat; SAFE≠quality; gold-substring≠gen; predicate/boolean LOOKUP = false-hit (BF-FOREVER even→add); type/coercion LOOKUP = false-hit (BE-FOREVER str→int→add); exact-gold ABSTAIN = miss (a.clear()); BA-FOREVER pow·mod·max·sort·len FH must stay 0; BB-FOREVER min·xor·absdiff·and·or FH must stay 0; BC-FOREVER floordiv·neg·gcd·lshift·rshift·nand FH must stay 0; BD-FOREVER reverse≠f-string · mul≠add FH must stay 0; BE-FOREVER str→int / type-coercion FH must stay 0; AZ hold div·sub·BIP FH must stay 0; BA…BE PASS with BF FP = PACK THEATER; truncate-to-span≠gen IQ; DECODE gibberish≠content_ok; eval path = prod ask path; generative bar = BF5 only under written method plan; no NANOGEN16 without M1|M2|M3 plan; no CTX/SMART/FAST clone; no invent Wave BG without lab-book reopen; prefer predicate/schema gate over bank stuffing; prefer HOLD/SKIP over fake PROMOTE

Next: **BF4 H-CTXBF** — context content bars without FP regress.
