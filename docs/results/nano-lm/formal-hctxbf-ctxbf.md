# H-CTXBF (BF4) — howto·cite·long content + anti-FP (**DONE** — PROMOTE)

> Lab: `.local/pesquisa.md` §3 · §9 BF4 · Session: `.local/wave-bf/SESSION.md`  
> Parent: [formal-hfastbf-fastbf.md](formal-hfastbf-fastbf.md) · BF0 ctx baseline (= H-CTXBE / H-CTXGAIN / H-CTXLIFT2)  
> Module: `nano_lm/src/ctxbf_ops.py` · Runner: `npm run nano:ctxbf`  
> **Not** BE [formal-hctxbe-ctxbe.md](formal-hctxbe-ctxbe.md) (`npm run nano:ctxbe`) · **Not** BD [formal-hctxgain-ctxgain.md](formal-hctxgain-ctxgain.md) · **Not** AH/BC/BB/BA CTX archives

## Hypothesis

Hold/improve usable long/cite/howto context content bars on prod path; PROMOTE only if content_ok on frozen pack + apps smoke, §1 anti-FP holds (BF-FOREVER FH 0 · BA…BE forever hold · AZ hold · over-refuse 0 · live FP 0), p50/p99 published, modes 4/4 — L_eff alone ≠ win; ≠ BE H-CTXBE archive · ≠ BD H-CTXGAIN · ≠ AH H-CTXLIFT · ≠ BC H-CTXLIFT2 · ≠ BB H-CTXHOLD · ≠ BA H-CTXREAL2

## Gate

| Metric | Result | Bar |
|--------|-------:|-----|
| ctx_content_ok | **5/5** (howto=True cite=True long=True) | all |
| apps_content_ok | **True** (3) | true |
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
| PEAK | **0.009330000011686934** | **0.04281129000446533** | 128 |
| DECODE | **10.99521549997462** | **11.607431670042843** | 12 |
| ABSTAIN | **91.37129499998764** | **115.23802333000961** | 32 |

## Finding

1. Howto·cite·long content bars held on frozen pack + apps smoke.  
2. L_eff alone ≠ win (content bars required).  
3. Anti-FP hold: BF FH 0 · BE…BA forever · AZ · over-refuse 0 · live FP 0.  
4. Prod tetrad p50/p99 published under max safe CPU (`cpus-6`, workers≤6).  
5. Wall clock ~10.7s.  
6. BE/BD/AH/BC/BB/BA CTX archives untouched.  
7. Generative claim still locked (gen stance SKIP; H-NANOGEN16 not opened).

## Reproduce

```bash
npm run nano:ctxbf
npm run nano:fastbf
# ≠ BE archive: npm run nano:ctxbe
```

## Artifacts

- Summary: `results/nano-lm/wave-bf/ctxbf_summary.json`  
- Contract: `nano_lm/tests/test_ctxbf.py`

## Claims

| Allowed | Forbidden |
|---------|-----------|
| AF packaged stack + AQ product layer + AS trust path + ablated DECODE (snippet-prefix + gibberish-tail STRICT) — not unlabeled open chat LM · not TAC unlocked | Open chat / mini-AGI |
| Content bars as ctx win | L_eff alone as pass |
| Anti-FP hold required | Trade FP for ctx |
| BE/BD/AH/BC/BB/BA CTX archives stay | Rewrite formal-hctxbe |

SAFE note: SAFE / ADVSAFE false-hit score ≠ answer quality; SAFE = no wrong gold only (anti-FP); pack FH 0 ≠ forever held-out generalization; predicate/boolean wrong-bank LOOKUP = false-hit (even→def add); BA…BE forever PASS with BF-FOREVER FP = PACK THEATER; exact-gold ABSTAIN = product miss; gold-substring / gibberish-tail / span-fallback ≠ generative PROMOTE  
Anti-FP: LOOKUP|PEAK|DECODE|ABSTAIN labeled; never LOOKUP-as-IQ; never peak-as-open-chat; SAFE≠quality; gold-substring≠gen; predicate/boolean LOOKUP = false-hit (BF-FOREVER even→add); type/coercion LOOKUP = false-hit (BE-FOREVER str→int→add); exact-gold ABSTAIN = miss (a.clear()); BA-FOREVER pow·mod·max·sort·len FH must stay 0; BB-FOREVER min·xor·absdiff·and·or FH must stay 0; BC-FOREVER floordiv·neg·gcd·lshift·rshift·nand FH must stay 0; BD-FOREVER reverse≠f-string · mul≠add FH must stay 0; BE-FOREVER str→int / type-coercion FH must stay 0; AZ hold div·sub·BIP FH must stay 0; BA…BE PASS with BF FP = PACK THEATER; truncate-to-span≠gen IQ; DECODE gibberish≠content_ok; eval path = prod ask path; generative bar = BF5 only under written method plan; no NANOGEN16 without M1|M2|M3 plan; no CTX/SMART/FAST clone; no invent Wave BG without lab-book reopen; prefer predicate/schema gate over bank stuffing; prefer HOLD/SKIP over fake PROMOTE

Next: **BF5 H-NANOGEN16 or SKIP** — only with written M1|M2|M3; else SKIP.
