# H-FASTLIFT (BC2) — prod p50/p99 + anti-FP hold (**DONE** — PROMOTE)

> Lab: `.local/pesquisa.md` §3 · §9 BC2 · Session: `.local/wave-bc/SESSION.md`  
> Parent: [formal-hopsfam-opsfam.md](formal-hopsfam-opsfam.md) · BC0 speed baseline (= BB H-FASTHOLD)  
> Module: `nano_lm/src/bc_fastlift_ops.py` · Runner: `npm run nano:bc:fastlift`  
> **Not** AH [formal-hfastlift-fastlift.md](formal-hfastlift-fastlift.md) (`npm run nano:fastlift`) · **Not** BB [formal-hfasthold-fasthold.md](formal-hfasthold-fasthold.md) (`npm run nano:bb:fasthold`) · **Not** BA [formal-hfastreal-ba2.md](formal-hfastreal-ba2.md)

## Hypothesis

Hold/improve prod-ask p50/p99 for LOOKUP·PEAK·DECODE·ABSTAIN; PROMOTE only if §1 anti-FP holds (BC-FOREVER FH 0 · BA/BB forever hold · AZ hold · over-refuse 0 · live FP 0) and live p99 does not regress vs BC0/BB-FASTHOLD baseline — never warm-cache vanity; LOOKUP wall=0 ≠ speed IQ; sub-ms PEAK walls ≠ speed IQ; ≠ AH H-FASTLIFT archive · ≠ BB H-FASTHOLD rename · ≠ BA H-FASTREAL archive · ≠ FP-for-ms

## Gate

| Metric | Result | Bar |
|--------|-------:|-----|
| bc_forever_false_hit | **0** (18/18) | **0** |
| ba_forever_false_hit | **0** (15/15) | **0** |
| bb_forever_false_hit | **0** (15/15) | **0** |
| az_hold_false_hit | **0** (12/12) | **0** |
| overrefuse_miss | **0** (3/3) | **0** |
| live_fp | **0** | **0** |
| p99_regress | **False** ([]) | false (≤1.5× BB-FASTHOLD) |
| modes_visible | **ABSTAIN · DECODE · LOOKUP · PEAK** (4/4) | 4/4 |
| Decision | **PROMOTE** | — |

## Latency p50/p99 (prod ask path)

| Path | p50 wall_ms | p99 wall_ms | n |
|------|------------:|------------:|--:|
| LOOKUP | **0.0** | **0.0** | 64 |
| PEAK | **0.009197996405418962** | **0.04120658952160745** | 128 |
| DECODE | **10.685407502023736** | **11.968237772889552** | 12 |
| ABSTAIN | **92.71498299858649** | **130.66686314792605** | 32 |

Samples: LOOKUP=64 · PEAK=128 · DECODE=12 · ABSTAIN=32

## Finding

1. Prod-path tetrad measured under max safe CPU (`cpus-4`, workers≤8).  
2. LOOKUP wall=0 **and** sub-ms PEAK walls **not** sold as speed IQ (regress gate uses base p99 ≥1ms).  
3. Anti-FP hold: BC FH 0 · BA FH 0 · BB FH 0 · AZ hold · over-refuse 0 · live FP 0.  
4. Live product p99 (DECODE·ABSTAIN) checked vs BC0/BB-FASTHOLD (max ratio 1.5).  
5. Warm-cache vanity forbidden.  
6. Wall clock ~10.7s · workers parallel antifp packs.  
7. AH `nano:fastlift` · BB `nano:bb:fasthold` · BA `nano:ba:fastreal` archives untouched.  
8. Generative claim still locked (H-NANOGEN13 defer stance).

## Reproduce

```bash
npm run nano:bc:fastlift
npm run nano:opsfam
# ≠ AH archive: npm run nano:fastlift
# ≠ BB archive: npm run nano:bb:fasthold
```

## Artifacts

- Summary: `results/nano-lm/wave-bc/bc_fastlift_summary.json`  
- Contract: `nano_lm/tests/test_bc_fastlift.py`

## Claims

| Allowed | Forbidden |
|---------|-----------|
| AF packaged stack + AQ product layer + AS trust path + ablated DECODE (snippet-prefix + gibberish-tail STRICT) — not unlabeled open chat LM · not TAC unlocked | Open chat / mini-AGI |
| Publish prod p50/p99 | LOOKUP wall=0 as speed IQ |
| Anti-FP hold required | Trade FP for ms |
| BB-FASTHOLD baseline p99 | Warm-cache vanity as product win |
| AH/BB/BA FAST archives stay | Rewrite AH formal-hfastlift-fastlift |

SAFE note: SAFE / ADVSAFE false-hit score ≠ answer quality; SAFE = no wrong gold only (anti-FP); pack FH 0 ≠ forever held-out generalization; intent-mismatch LOOKUP = false-hit (floordiv/neg/gcd/lshift/rshift/nand); BA+BB forever PASS with BC-FOREVER FP = PACK THEATER; exact-gold ABSTAIN = product miss; gold-substring / gibberish-tail / span-fallback ≠ generative PROMOTE  
Anti-FP: LOOKUP|PEAK|DECODE|ABSTAIN labeled; never LOOKUP-as-IQ; never peak-as-open-chat; SAFE≠quality; gold-substring≠gen; intent-mismatch LOOKUP = false-hit (BC-FOREVER floordiv/neg/gcd/lshift/rshift/nand → add); exact-gold ABSTAIN = miss (a.clear()); BA-FOREVER pow·mod·max·sort·len FH must stay 0; BB-FOREVER min·xor·absdiff·and·or FH must stay 0; AZ hold div·sub·BIP FH must stay 0; BA+BB PASS with BC FP = PACK THEATER; truncate-to-span≠gen IQ; DECODE gibberish≠content_ok; eval path = prod ask path; generative bar = BC4 only under real new method; no NANOGEN13 = NANOGEN12+rename; no CTX/SMART/FAST clone; no invent Wave BD without lab-book reopen; prefer HOLD/defer over fake PROMOTE

Next: **BC3 H-CTXLIFT2** — context content bars without FP regress.
