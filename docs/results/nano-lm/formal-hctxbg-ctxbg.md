# H-CTXBG (BG4) — howto·cite·long content + anti-FP (**DONE** — PROMOTE)

> Lab: `.local/pesquisa.md` §3 · §9 BG4 · Session: `.local/wave-bg/SESSION.md`  
> Parent: [formal-hfastbg-fastbg.md](formal-hfastbg-fastbg.md) · BG0 ctx baseline (= H-CTXBF / H-CTXBE / H-CTXGAIN)  
> Module: `nano_lm/src/ctxbg_ops.py` · Runner: `npm run nano:ctxbg`  
> **Not** BF [formal-hctxbf-ctxbf.md](formal-hctxbf-ctxbf.md) (`npm run nano:ctxbf`) · **Not** BE/BD/AH/BC/BB/BA CTX archives

## Hypothesis

Hold/improve usable long/cite/howto context content bars on prod path; PROMOTE only if content_ok on frozen pack + apps smoke, §1 anti-FP holds (BG-FOREVER FH 0 · BA…BF forever hold · AZ hold · over-refuse 0 · live FP 0), p50/p99 published, modes 4/4 — L_eff alone ≠ win; ≠ BF H-CTXBF archive · ≠ BE H-CTXBE · ≠ BD H-CTXGAIN · ≠ AH H-CTXLIFT · ≠ BC H-CTXLIFT2 · ≠ BB H-CTXHOLD · ≠ BA H-CTXREAL2

## Gate

| Metric | Result | Bar |
|--------|-------:|-----|
| ctx_content_ok | **5/5** (howto=True cite=True long=True) | all |
| apps_content_ok | **True** (3) | true |
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
| modes_visible | **ABSTAIN · DECODE · LOOKUP · PEAK** (4/4) | 4/4 |
| Decision | **PROMOTE** | — |

## Latency p50/p99 (published · not sole win)

| Path | p50 wall_ms | p99 wall_ms | n |
|------|------------:|------------:|--:|
| LOOKUP | **0.0** | **0.0** | 64 |
| PEAK | **0.009294500159739982** | **0.018951679485326188** | 128 |
| DECODE | **10.950506498375034** | **11.321402130251954** | 12 |
| ABSTAIN | **96.04843900069682** | **216.0536445293474** | 32 |

## Finding

1. Howto·cite·long content bars held on frozen pack + apps smoke.  
2. L_eff alone ≠ win (content bars required).  
3. Anti-FP hold: BG FH 0 · BA…BF forever · AZ · over-refuse 0 · live FP 0.  
4. Prod tetrad p50/p99 published under max safe CPU (`cpus-6`, workers≤6).  
5. Wall clock ~9.1s.  
6. BF/BE/BD/AH/BC/BB/BA CTX archives untouched.  
7. Generative claim still locked (gen stance SKIP; H-NANOGEN17 not opened).

## Reproduce

```bash
npm run nano:ctxbg
npm run nano:fastbg
# ≠ BF archive: npm run nano:ctxbf
```

## Artifacts

- Summary: `results/nano-lm/wave-bg/ctxbg_summary.json`  
- Contract: `nano_lm/tests/test_ctxbg.py`

## Claims

| Allowed | Forbidden |
|---------|-----------|
| AF packaged stack + AQ product layer + AS trust path + ablated DECODE (snippet-prefix + gibberish-tail STRICT) — not unlabeled open chat LM · not TAC unlocked | Open chat / mini-AGI |
| Content bars as ctx win | L_eff alone as pass |
| Anti-FP hold required | Trade FP for ctx |
| BF/BE/BD/AH/BC/BB/BA CTX archives stay | Rewrite formal-hctxbf |

SAFE note: SAFE / ADVSAFE false-hit score ≠ answer quality; SAFE = no wrong gold only (anti-FP); pack FH 0 ≠ forever held-out generalization; unary/math/string-transform wrong-bank LOOKUP = false-hit (abs→def add · upper→f-string · all-truthy→clear); BA…BF forever PASS with BG-FOREVER FP = PACK THEATER; exact-gold ABSTAIN = product miss; gold-substring / gibberish-tail / span-fallback ≠ generative PROMOTE  
Anti-FP: LOOKUP|PEAK|DECODE|ABSTAIN labeled; never LOOKUP-as-IQ; never peak-as-open-chat; SAFE≠quality; gold-substring≠gen; unary/math LOOKUP = false-hit (BG-FOREVER abs/factorial→add); string-transform LOOKUP = false-hit (BG-FOREVER upper→f-string); aggregate/predicate LOOKUP = false-hit (all-truthy→clear); predicate/boolean LOOKUP = false-hit (BF-FOREVER even→add); type/coercion LOOKUP = false-hit (BE-FOREVER str→int→add); exact-gold ABSTAIN = miss (a.clear()); BA-FOREVER pow·mod·max·sort·len FH must stay 0; BB-FOREVER min·xor·absdiff·and·or FH must stay 0; BC-FOREVER floordiv·neg·gcd·lshift·rshift·nand FH must stay 0; BD-FOREVER reverse≠f-string · mul≠add FH must stay 0; BE-FOREVER str→int / type-coercion FH must stay 0; BF-FOREVER even/bool ≠ add FH must stay 0; AZ hold div·sub·BIP FH must stay 0; BA…BF PASS with BG FP = PACK THEATER; truncate-to-span≠gen IQ; DECODE gibberish≠content_ok; eval path = prod ask path; generative bar = BG5 only under written method plan; no NANOGEN17 without M1|M2|M3 plan; no CTX/SMART/FAST clone; no invent Wave BH without lab-book reopen; prefer unary/transform/arity gate over bank stuffing; prefer HOLD/SKIP over fake PROMOTE

Next: **BG5 H-NANOGEN17 or SKIP** — only with written M1|M2|M3; else SKIP.
