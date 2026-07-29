# H-FASTBG (BG3) — prod p50/p99 + anti-FP hold (**DONE** — PROMOTE)

> Lab: `.local/pesquisa.md` §4 · §9 BG3 · Session: `.local/wave-bg/SESSION.md`  
> Parent: [formal-hshippub-shippub.md](formal-hshippub-shippub.md) · BG0 speed baseline (= H-FASTBF)  
> Module: `nano_lm/src/fastbg_ops.py` · Runner: `npm run nano:fastbg`  
> **Not** BF [formal-hfastbf-fastbf.md](formal-hfastbf-fastbf.md) (`npm run nano:fastbf`) · **Not** BE/BD/AH/BC/BB FAST archives

## Hypothesis

Hold/improve prod-ask p50/p99 for LOOKUP·PEAK·DECODE·ABSTAIN; PROMOTE only if §1 anti-FP holds (BG-FOREVER FH 0 · BA…BF forever hold · AZ hold · over-refuse 0 · live FP 0) and live p99 does not regress vs BG0/H-FASTBF baseline — never warm-cache vanity; LOOKUP wall=0 ≠ speed IQ; sub-ms PEAK walls ≠ speed IQ; ≠ BF H-FASTBF archive · ≠ BE H-FASTBE · ≠ BD H-FASTGAIN · ≠ BC/AH H-FASTLIFT · ≠ BB H-FASTHOLD · ≠ BA H-FASTREAL · ≠ FP-for-ms

## Gate

| Metric | Result | Bar |
|--------|-------:|-----|
| bg_forever_false_hit | **0** (12/12) | **0** |
| bf_forever_false_hit | **0** (12/12) | **0** |
| be_forever_false_hit | **0** (12/12) | **0** |
| bd_forever_false_hit | **0** (12/12) | **0** |
| ba_forever_false_hit | **0** (15/15) | **0** |
| bb_forever_false_hit | **0** (15/15) | **0** |
| bc_forever_false_hit | **0** (18/18) | **0** |
| az_hold_false_hit | **0** (12/12) | **0** |
| overrefuse_miss | **0** (3/3) | **0** |
| live_fp | **0** | **0** |
| p99_regress | **False** ([]) | false (≤1.5× H-FASTBF) |
| modes_visible | **ABSTAIN · DECODE · LOOKUP · PEAK** (4/4) | 4/4 |
| Decision | **PROMOTE** | — |

## Latency p50/p99 (prod ask path)

| Path | p50 wall_ms | p99 wall_ms | n |
|------|------------:|------------:|--:|
| LOOKUP | **0.0** | **0.0** | 64 |
| PEAK | **0.00946950012803427** | **0.0158115696922323** | 128 |
| DECODE | **11.218205999739439** | **11.963300369861827** | 12 |
| ABSTAIN | **101.5883774998656** | **142.08108759017705** | 32 |

Samples: LOOKUP=64 · PEAK=128 · DECODE=12 · ABSTAIN=32

## Finding

1. Prod-path tetrad measured under max safe CPU (`cpus-4`, workers≤6).  
2. LOOKUP wall=0 **and** sub-ms PEAK walls **not** sold as speed IQ.  
3. Anti-FP hold: BG FH 0 · BA…BF forever · AZ hold · over-refuse 0 · live FP 0.  
4. Live product p99 (DECODE·ABSTAIN) checked vs BG0/H-FASTBF (max ratio 1.5).  
5. Warm-cache vanity forbidden.  
6. Wall clock ~11.1s · workers parallel antifp packs.  
7. BF `nano:fastbf` · BE/BD/AH/BC/BB FAST archives untouched.  
8. Generative claim still locked (gen stance SKIP; H-NANOGEN17 not opened).

## Reproduce

```bash
npm run nano:fastbg
npm run nano:unaryint
# ≠ BF archive: npm run nano:fastbf
```

## Artifacts

- Summary: `results/nano-lm/wave-bg/fastbg_summary.json`  
- Contract: `nano_lm/tests/test_fastbg.py`

## Claims

| Allowed | Forbidden |
|---------|-----------|
| AF packaged stack + AQ product layer + AS trust path + ablated DECODE (snippet-prefix + gibberish-tail STRICT) — not unlabeled open chat LM · not TAC unlocked | Open chat / mini-AGI |
| Publish prod p50/p99 | LOOKUP wall=0 as speed IQ |
| Anti-FP hold required | Trade FP for ms |
| H-FASTBF baseline p99 | Warm-cache vanity as product win |
| BF/BE/BD/AH/BC/BB FAST archives stay | Rewrite BF formal-hfastbf |

SAFE note: SAFE / ADVSAFE false-hit score ≠ answer quality; SAFE = no wrong gold only (anti-FP); pack FH 0 ≠ forever held-out generalization; unary/math/string-transform wrong-bank LOOKUP = false-hit (abs→def add · upper→f-string · all-truthy→clear); BA…BF forever PASS with BG-FOREVER FP = PACK THEATER; exact-gold ABSTAIN = product miss; gold-substring / gibberish-tail / span-fallback ≠ generative PROMOTE  
Anti-FP: LOOKUP|PEAK|DECODE|ABSTAIN labeled; never LOOKUP-as-IQ; never peak-as-open-chat; SAFE≠quality; gold-substring≠gen; unary/math LOOKUP = false-hit (BG-FOREVER abs/factorial→add); string-transform LOOKUP = false-hit (BG-FOREVER upper→f-string); aggregate/predicate LOOKUP = false-hit (all-truthy→clear); predicate/boolean LOOKUP = false-hit (BF-FOREVER even→add); type/coercion LOOKUP = false-hit (BE-FOREVER str→int→add); exact-gold ABSTAIN = miss (a.clear()); BA-FOREVER pow·mod·max·sort·len FH must stay 0; BB-FOREVER min·xor·absdiff·and·or FH must stay 0; BC-FOREVER floordiv·neg·gcd·lshift·rshift·nand FH must stay 0; BD-FOREVER reverse≠f-string · mul≠add FH must stay 0; BE-FOREVER str→int / type-coercion FH must stay 0; BF-FOREVER even/bool ≠ add FH must stay 0; AZ hold div·sub·BIP FH must stay 0; BA…BF PASS with BG FP = PACK THEATER; truncate-to-span≠gen IQ; DECODE gibberish≠content_ok; eval path = prod ask path; generative bar = BG5 only under written method plan; no NANOGEN17 without M1|M2|M3 plan; no CTX/SMART/FAST clone; no invent Wave BH without lab-book reopen; prefer unary/transform/arity gate over bank stuffing; prefer HOLD/SKIP over fake PROMOTE

Next: **BG4 H-CTXBG** — context content bars without FP regress.
