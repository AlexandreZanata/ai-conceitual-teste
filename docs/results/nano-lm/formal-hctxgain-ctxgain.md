# H-CTXGAIN (BD3) — howto·cite·long content + anti-FP (**DONE** — PROMOTE)

> Lab: `.local/pesquisa.md` §3 · §9 BD3 · Session: `.local/wave-bd/SESSION.md`  
> Parent: [formal-hfastgain-fastgain.md](formal-hfastgain-fastgain.md) · BD0 ctx baseline (= H-CTXLIFT2 / H-CTXHOLD)  
> Module: `nano_lm/src/bd_ctxgain_ops.py` · Runner: `npm run nano:bd:ctxgain`  
> **Not** AH [formal-hctxlift-ctxlift.md](formal-hctxlift-ctxlift.md) · **Not** BC [formal-hctxlift2-ctxlift2.md](formal-hctxlift2-ctxlift2.md) (`npm run nano:bc:ctxlift2`) · **Not** BB [formal-hctxhold-ctxhold.md](formal-hctxhold-ctxhold.md)

## Hypothesis

Hold/improve usable long/cite/howto context content bars on prod path; PROMOTE only if content_ok on frozen pack + apps smoke, §1 anti-FP holds (BD-FOREVER FH 0 · BA/BB/BC forever hold · AZ hold · over-refuse 0 · live FP 0), p50/p99 published, modes 4/4 — L_eff alone ≠ win; ≠ AH H-CTXLIFT archive · ≠ BC H-CTXLIFT2 rename · ≠ BB H-CTXHOLD archive · ≠ BA H-CTXREAL2 archive

## Gate

| Metric | Result | Bar |
|--------|-------:|-----|
| ctx_content_ok | **5/5** (howto=True cite=True long=True) | all |
| apps_content_ok | **True** (3) | true |
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
| PEAK | **0.009090999810723588** | **0.015504563998547397** | 128 |
| DECODE | **11.342784498992842** | **13.090273359484854** | 12 |
| ABSTAIN | **93.30542399766273** | **120.78460808843377** | 32 |

## Finding

1. Howto·cite·long content bars held on frozen pack + apps smoke.  
2. L_eff alone ≠ win (content bars required).  
3. Anti-FP hold: BD FH 0 · BA FH 0 · BB FH 0 · BC FH 0 · AZ · over-refuse 0 · live FP 0.  
4. Prod tetrad p50/p99 published under max safe CPU (`cpus-4`, workers≤8).  
5. Wall clock ~10.6s.  
6. AH/BC/BB/BA CTX archives untouched.  
7. Generative claim still locked (H-NANOGEN14 defer stance).

## Reproduce

```bash
npm run nano:bd:ctxgain
npm run nano:bd:fastgain
# ≠ BC archive: npm run nano:bc:ctxlift2
```

## Artifacts

- Summary: `results/nano-lm/wave-bd/bd_ctxgain_summary.json`  
- Contract: `nano_lm/tests/test_bd_ctxgain.py`

## Claims

| Allowed | Forbidden |
|---------|-----------|
| AF packaged stack + AQ product layer + AS trust path + ablated DECODE (snippet-prefix + gibberish-tail STRICT) — not unlabeled open chat LM · not TAC unlocked | Open chat / mini-AGI |
| Content bars as ctx win | L_eff alone as pass |
| Anti-FP hold required | Trade FP for ctx |
| AH/BC/BB/BA CTX archives stay | Rewrite formal-hctxlift2 |

SAFE note: SAFE / ADVSAFE false-hit score ≠ answer quality; SAFE = no wrong gold only (anti-FP); pack FH 0 ≠ forever held-out generalization; semantic wrong-bank LOOKUP = false-hit (reverse→f-string · mul→add); BA+BB+BC forever PASS with BD-FOREVER FP = PACK THEATER; exact-gold ABSTAIN = product miss; gold-substring / gibberish-tail / span-fallback ≠ generative PROMOTE  
Anti-FP: LOOKUP|PEAK|DECODE|ABSTAIN labeled; never LOOKUP-as-IQ; never peak-as-open-chat; SAFE≠quality; gold-substring≠gen; semantic wrong-bank LOOKUP = false-hit (BD-FOREVER reverse→f-string / mul→add); exact-gold ABSTAIN = miss (a.clear()); BA-FOREVER pow·mod·max·sort·len FH must stay 0; BB-FOREVER min·xor·absdiff·and·or FH must stay 0; BC-FOREVER floordiv·neg·gcd·lshift·rshift·nand FH must stay 0; AZ hold div·sub·BIP FH must stay 0; BA+BB+BC PASS with BD FP = PACK THEATER; truncate-to-span≠gen IQ; DECODE gibberish≠content_ok; eval path = prod ask path; generative bar = BD4 only under real new method; no NANOGEN14 = NANOGEN13+rename; no CTX/SMART/FAST clone; no invent Wave BE without lab-book reopen; prefer HOLD/defer over fake PROMOTE

Next: **BD4 H-NANOGEN14** — one real method or HOLD/DEFER.
