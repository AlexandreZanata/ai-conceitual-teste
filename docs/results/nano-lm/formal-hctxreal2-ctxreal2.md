# H-CTXREAL2 — usable long/cite/howto (**DONE** — PROMOTE)

> Lab: `.local/pesquisa.md` §2 · §8 BA3 · Session: `.local/wave-ba/SESSION.md`  
> Parent: [formal-hfastreal-ba2.md](formal-hfastreal-ba2.md) · BA0 ctx baseline  
> Module: `nano_lm/src/ba_ctxreal2_ops.py` · Runner: `npm run nano:ba:ctxreal2`  
> **Not** AG archive [formal-hctxreal-ctxreal.md](formal-hctxreal-ctxreal.md) (`npm run nano:ctxreal`)

## Hypothesis

Publish usable long/cite/howto context content bars on prod path; PROMOTE only if content_ok on frozen pack + apps smoke, §1 anti-FP holds (forever FH 0 · AZ hold · over-refuse 0 · live FP 0), p50/p99 published, modes 4/4 — L_eff alone ≠ win; ≠ AG H-CTXREAL quad-doc L_eff archive

## Gate

| Metric | Result | Bar |
|--------|-------:|-----|
| ctx_content_ok | **5/5** | all |
| howto_ok / cite_ok / long_ok | **True** / **True** / **True** | True |
| apps_content_ok | **True** (3) | known·howto·long-doc |
| forever_false_hit | **0** (15/15) | **0** |
| az_hold_false_hit | **0** (12/12) | **0** |
| overrefuse_miss | **0** (3/3) | **0** |
| live_fp | **0** | **0** |
| modes_visible | **ABSTAIN · DECODE · LOOKUP · PEAK** (4/4) | 4/4 |
| Decision | **PROMOTE** | — |

## Latency p50/p99 (republish)

| Path | p50 wall_ms | p99 wall_ms |
|------|------------:|------------:|
| LOOKUP | **0.0** | **0.0** |
| PEAK | **0.02046049849013798** | **0.032600638660369455** |
| DECODE | **11.264537497481797** | **11.819363079121104** |
| ABSTAIN | **95.03086200129474** | **122.22758313248053** |

## Finding

1. Frozen howto·cite·long content pack scored on prod path.  
2. Apps known-ask · howto · long-doc LOOKUP gold held.  
3. REALGAIN anti-FP hold: forever FH 0 · AZ hold · over-refuse 0.  
4. p50/p99 republished; L_eff alone **not** a win.  
5. Wall clock ~10.5s · max safe CPU (`cpus-4`).  
6. AG H-CTXREAL quad-doc L_eff archive untouched (`npm run nano:ctxreal`).  
7. Generative claim still locked (gen stance defer).  

## Reproduce

```bash
npm run nano:ba:ctxreal2
npm run nano:test && npm run verify
```

## Artifacts

- Summary: `results/nano-lm/wave-ba/ba_ctxreal2_summary.json`  
- Contract: `nano_lm/tests/test_ba_ctxreal2.py`

## Claims

| Allowed | Forbidden |
|---------|-----------|
| AF packaged stack + AQ product layer + AS trust path + ablated DECODE (snippet-prefix + gibberish-tail STRICT) — not unlabeled open chat LM · not TAC unlocked | Open chat / mini-AGI |
| Usable howto·cite·long content | L_eff alone as ctx win |
| Eval path = prod ask path | LOOKUP-as-IQ · pack theater |

SAFE note: SAFE / ADVSAFE false-hit score ≠ answer quality; SAFE = no wrong gold only (anti-FP); pack FH 0 ≠ forever held-out generalization; intent-mismatch LOOKUP = false-hit (pow/mod/max/sort/len); exact-gold ABSTAIN = product miss; gold-substring / gibberish-tail / span-fallback ≠ generative PROMOTE  
Anti-FP: LOOKUP|PEAK|DECODE|ABSTAIN labeled; never LOOKUP-as-IQ; never peak-as-open-chat; SAFE≠quality; gold-substring≠gen; intent-mismatch LOOKUP = false-hit (BA-FOREVER pow/mod/max/sort/len); exact-gold ABSTAIN = miss (a.clear()); AZ hold div·sub·BIP FH must stay 0; truncate-to-span≠gen IQ; DECODE gibberish≠content_ok; eval path = prod ask path; pack PASS with forever FP = PACK THEATER; generative bar = BA4 only under real new method; no NANOGEN11 = NANOGEN10+rename; no CTX/SMART/FAST clone; no invent Wave BB without lab-book reopen; prefer HOLD/defer over fake PROMOTE

Next: **BA4 H-NANOGEN11** — one real gen method or HOLD/DEFER.
