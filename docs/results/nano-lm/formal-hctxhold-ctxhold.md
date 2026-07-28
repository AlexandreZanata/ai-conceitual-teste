# H-CTXHOLD — usable long/cite/howto (**DONE** — PROMOTE)

> Lab: `.local/pesquisa.md` §2 · §8 BB3 · Session: `.local/wave-bb/SESSION.md`  
> Parent: [formal-hfasthold-fasthold.md](formal-hfasthold-fasthold.md) · BB0 ctx baseline (= BA H-CTXREAL2)  
> Module: `nano_lm/src/bb_ctxhold_ops.py` · Runner: `npm run nano:bb:ctxhold`  
> **Not** BA [formal-hctxreal2-ctxreal2.md](formal-hctxreal2-ctxreal2.md) (`npm run nano:ba:ctxreal2`) · **Not** AG [formal-hctxreal-ctxreal.md](formal-hctxreal-ctxreal.md) (`npm run nano:ctxreal`)

## Hypothesis

Hold/improve usable long/cite/howto context content bars on prod path; PROMOTE only if content_ok on frozen pack + apps smoke, §1 anti-FP holds (BB-FOREVER FH 0 · BA-FOREVER hold · AZ hold · over-refuse 0 · live FP 0), p50/p99 published, modes 4/4 — L_eff alone ≠ win; ≠ BA H-CTXREAL2 rename · ≠ AG H-CTXREAL archive

## Gate

| Metric | Result | Bar |
|--------|-------:|-----|
| ctx_content_ok | **5/5** | all |
| howto_ok / cite_ok / long_ok | **True** / **True** / **True** | True |
| apps_content_ok | **True** (3) | known·howto·long-doc |
| bb_forever_false_hit | **0** (15/15) | **0** |
| ba_forever_false_hit | **0** (15/15) | **0** |
| az_hold_false_hit | **0** (12/12) | **0** |
| overrefuse_miss | **0** (3/3) | **0** |
| live_fp | **0** | **0** |
| modes_visible | **ABSTAIN · DECODE · LOOKUP · PEAK** (4/4) | 4/4 |
| Decision | **PROMOTE** | — |

## Latency p50/p99 (republish)

| Path | p50 wall_ms | p99 wall_ms |
|------|------------:|------------:|
| LOOKUP | **0.0** | **0.0** |
| PEAK | **0.009407496690982953** | **0.03530991845764222** |
| DECODE | **10.974694003380137** | **18.303889243616144** |
| ABSTAIN | **92.60646000257111** | **132.826057871207** |

## Finding

1. Frozen howto·cite·long content pack scored on prod path.  
2. Apps known-ask · howto · long-doc LOOKUP gold held.  
3. INTENTGEN anti-FP hold: BB FH 0 · BA FH 0 · AZ hold · over-refuse 0.  
4. p50/p99 republished; L_eff alone **not** a win.  
5. Wall clock ~10.6s · max safe CPU (`cpus-6`, workers≤6).  
6. BA `nano:ba:ctxreal2` + AG `nano:ctxreal` archives untouched.  
7. Generative claim still locked (H-NANOGEN12 defer stance).  

## Reproduce

```bash
npm run nano:bb:ctxhold
npm run nano:test && npm run verify
# ≠ BA archive: npm run nano:ba:ctxreal2
# ≠ AG archive: npm run nano:ctxreal
```

## Artifacts

- Summary: `results/nano-lm/wave-bb/bb_ctxhold_summary.json`  
- Contract: `nano_lm/tests/test_bb_ctxhold.py`

## Claims

| Allowed | Forbidden |
|---------|-----------|
| AF packaged stack + AQ product layer + AS trust path + ablated DECODE (snippet-prefix + gibberish-tail STRICT) — not unlabeled open chat LM · not TAC unlocked | Open chat / mini-AGI |
| Usable howto·cite·long content | L_eff alone as ctx win |
| Eval path = prod ask path | LOOKUP-as-IQ · pack theater |
| BA/AG CTX archives stay | Rewrite BA/AG formal-hctxreal* |

SAFE note: SAFE / ADVSAFE false-hit score ≠ answer quality; SAFE = no wrong gold only (anti-FP); pack FH 0 ≠ forever held-out generalization; intent-mismatch LOOKUP = false-hit (min/xor/absdiff/and/or); BA-FOREVER PASS with BB-FOREVER FP = PACK THEATER; exact-gold ABSTAIN = product miss; gold-substring / gibberish-tail / span-fallback ≠ generative PROMOTE  
Anti-FP: LOOKUP|PEAK|DECODE|ABSTAIN labeled; never LOOKUP-as-IQ; never peak-as-open-chat; SAFE≠quality; gold-substring≠gen; intent-mismatch LOOKUP = false-hit (BB-FOREVER min/xor/absdiff/and/or → add); exact-gold ABSTAIN = miss (a.clear()); BA-FOREVER pow·mod·max·sort·len FH must stay 0; AZ hold div·sub·BIP FH must stay 0; BA PASS with BB FP = PACK THEATER; truncate-to-span≠gen IQ; DECODE gibberish≠content_ok; eval path = prod ask path; generative bar = BB4 only under real new method; no NANOGEN12 = NANOGEN11+rename; no CTX/SMART/FAST clone; no invent Wave BC without lab-book reopen; prefer HOLD/defer over fake PROMOTE

Next: **BB4 H-NANOGEN12** — one real gen method or HOLD/DEFER.
