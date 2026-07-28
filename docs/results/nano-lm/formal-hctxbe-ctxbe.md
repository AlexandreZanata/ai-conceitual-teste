# H-CTXBE (BE4) — howto·cite·long content + anti-FP (**DONE** — PROMOTE)

> Lab: `.local/pesquisa.md` §3 · §9 BE4 · Session: `.local/wave-be/SESSION.md`  
> Parent: [formal-hfastbe-fastbe.md](formal-hfastbe-fastbe.md) · BE0 ctx baseline (= H-CTXGAIN / H-CTXLIFT2 / H-CTXHOLD)  
> Module: `nano_lm/src/ctxbe_ops.py` · Runner: `npm run nano:ctxbe`  
> **Not** BD [formal-hctxgain-ctxgain.md](formal-hctxgain-ctxgain.md) (`npm run nano:bd:ctxgain`) · **Not** AH [formal-hctxlift-ctxlift.md](formal-hctxlift-ctxlift.md) · **Not** BC [formal-hctxlift2-ctxlift2.md](formal-hctxlift2-ctxlift2.md) (`npm run nano:bc:ctxlift2`) · **Not** BB [formal-hctxhold-ctxhold.md](formal-hctxhold-ctxhold.md)

## Hypothesis

Hold/improve usable long/cite/howto context content bars on prod path; PROMOTE only if content_ok on frozen pack + apps smoke, §1 anti-FP holds (BE-FOREVER FH 0 · BA…BD forever hold · AZ hold · over-refuse 0 · live FP 0), p50/p99 published, modes 4/4 — L_eff alone ≠ win; ≠ BD H-CTXGAIN archive · ≠ AH H-CTXLIFT · ≠ BC H-CTXLIFT2 · ≠ BB H-CTXHOLD · ≠ BA H-CTXREAL2

## Gate

| Metric | Result | Bar |
|--------|-------:|-----|
| ctx_content_ok | **5/5** (howto=True cite=True long=True) | all |
| apps_content_ok | **True** (3) | true |
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
| PEAK | **0.02071200287900865** | **0.030377880320884287** | 128 |
| DECODE | **11.119874499854632** | **11.477947210660204** | 12 |
| ABSTAIN | **94.76194300077623** | **122.93563246130364** | 32 |

## Finding

1. Howto·cite·long content bars held on frozen pack + apps smoke.  
2. L_eff alone ≠ win (content bars required).  
3. Anti-FP hold: BE FH 0 · BD FH 0 · BA FH 0 · BB FH 0 · BC FH 0 · AZ · over-refuse 0 · live FP 0.  
4. Prod tetrad p50/p99 published under max safe CPU (`cpus-6`, workers≤6).  
5. Wall clock ~10.8s.  
6. BD/AH/BC/BB/BA CTX archives untouched.  
7. Generative claim still locked (H-NANOGEN15 defer-once stance).

## Reproduce

```bash
npm run nano:ctxbe
npm run nano:fastbe
# ≠ BD archive: npm run nano:bd:ctxgain
```

## Artifacts

- Summary: `results/nano-lm/wave-be/ctxbe_summary.json`  
- Contract: `nano_lm/tests/test_ctxbe.py`

## Claims

| Allowed | Forbidden |
|---------|-----------|
| AF packaged stack + AQ product layer + AS trust path + ablated DECODE (snippet-prefix + gibberish-tail STRICT) — not unlabeled open chat LM · not TAC unlocked | Open chat / mini-AGI |
| Content bars as ctx win | L_eff alone as pass |
| Anti-FP hold required | Trade FP for ctx |
| BD/AH/BC/BB/BA CTX archives stay | Rewrite formal-hctxgain |

SAFE note: SAFE / ADVSAFE false-hit score ≠ answer quality; SAFE = no wrong gold only (anti-FP); pack FH 0 ≠ forever held-out generalization; type/coercion wrong-bank LOOKUP = false-hit (str→int→def add); BA…BD forever PASS with BE-FOREVER FP = PACK THEATER; exact-gold ABSTAIN = product miss; gold-substring / gibberish-tail / span-fallback ≠ generative PROMOTE  
Anti-FP: LOOKUP|PEAK|DECODE|ABSTAIN labeled; never LOOKUP-as-IQ; never peak-as-open-chat; SAFE≠quality; gold-substring≠gen; type/coercion LOOKUP = false-hit (BE-FOREVER str→int→add); exact-gold ABSTAIN = miss (a.clear()); BA-FOREVER pow·mod·max·sort·len FH must stay 0; BB-FOREVER min·xor·absdiff·and·or FH must stay 0; BC-FOREVER floordiv·neg·gcd·lshift·rshift·nand FH must stay 0; BD-FOREVER reverse≠f-string · mul≠add FH must stay 0; AZ hold div·sub·BIP FH must stay 0; BA…BD PASS with BE FP = PACK THEATER; truncate-to-span≠gen IQ; DECODE gibberish≠content_ok; eval path = prod ask path; generative bar = BE5 only under real new method; no NANOGEN15 = NANOGEN14+rename; no CTX/SMART/FAST clone; no invent Wave BF without lab-book reopen; prefer compositional gate over bank stuffing; prefer HOLD/defer over fake PROMOTE

Next: **BE5 H-NANOGEN15** — one real method or DEFER once.
