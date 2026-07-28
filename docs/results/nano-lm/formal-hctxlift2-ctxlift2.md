# H-CTXLIFT2 (BC3) — usable long/cite/howto (**DONE** — PROMOTE)

> Lab: `.local/pesquisa.md` §3 · §9 BC3 · Session: `.local/wave-bc/SESSION.md`  
> Parent: [formal-hfastlift-bc2.md](formal-hfastlift-bc2.md) · BC0 ctx baseline (= BB H-CTXHOLD / BA H-CTXREAL2)  
> Module: `nano_lm/src/bc_ctxlift2_ops.py` · Runner: `npm run nano:bc:ctxlift2`  
> **Not** AH [formal-hctxlift-ctxlift.md](formal-hctxlift-ctxlift.md) (`npm run nano:ctxlift`) · **Not** BB [formal-hctxhold-ctxhold.md](formal-hctxhold-ctxhold.md) (`npm run nano:bb:ctxhold`) · **Not** BA [formal-hctxreal2-ctxreal2.md](formal-hctxreal2-ctxreal2.md)

## Hypothesis

Hold/improve usable long/cite/howto context content bars on prod path; PROMOTE only if content_ok on frozen pack + apps smoke, §1 anti-FP holds (BC-FOREVER FH 0 · BA/BB forever hold · AZ hold · over-refuse 0 · live FP 0), p50/p99 published, modes 4/4 — L_eff alone ≠ win; ≠ AH H-CTXLIFT archive · ≠ BB H-CTXHOLD rename · ≠ BA H-CTXREAL2 archive

## Gate

| Metric | Result | Bar |
|--------|-------:|-----|
| ctx_content_ok | **5/5** | all |
| howto_ok / cite_ok / long_ok | **True** / **True** / **True** | True |
| apps_content_ok | **True** (3) | known·howto·long-doc |
| bc_forever_false_hit | **0** (18/18) | **0** |
| ba_forever_false_hit | **0** (15/15) | **0** |
| bb_forever_false_hit | **0** (15/15) | **0** |
| az_hold_false_hit | **0** (12/12) | **0** |
| overrefuse_miss | **0** (3/3) | **0** |
| live_fp | **0** | **0** |
| modes_visible | **ABSTAIN · DECODE · LOOKUP · PEAK** (4/4) | 4/4 |
| Decision | **PROMOTE** | — |

## Latency p50/p99 (republish)

| Path | p50 wall_ms | p99 wall_ms |
|------|------------:|------------:|
| LOOKUP | **0.0** | **0.0** |
| PEAK | **0.020427996787475422** | **0.0302675105194794** |
| DECODE | **10.86839600247913** | **12.394394534567255** |
| ABSTAIN | **94.8239490026026** | **170.35499931342207** |

## Finding

1. Frozen howto·cite·long content pack scored on prod path.  
2. Apps known-ask · howto · long-doc LOOKUP gold held.  
3. Anti-FP hold: BC FH 0 · BA FH 0 · BB FH 0 · AZ hold · over-refuse 0.  
4. p50/p99 republished; L_eff alone **not** a win.  
5. Wall clock ~11.0s · max safe CPU (`cpus-4`, workers≤8).  
6. AH `nano:ctxlift` · BB `nano:bb:ctxhold` · BA `nano:ba:ctxreal2` archives untouched.  
7. Generative claim still locked (H-NANOGEN13 defer stance).  

## Reproduce

```bash
npm run nano:bc:ctxlift2
npm run nano:test && npm run verify
# ≠ AH archive: npm run nano:ctxlift
# ≠ BB archive: npm run nano:bb:ctxhold
```

## Artifacts

- Summary: `results/nano-lm/wave-bc/bc_ctxlift2_summary.json`  
- Contract: `nano_lm/tests/test_bc_ctxlift2.py`

## Claims

| Allowed | Forbidden |
|---------|-----------|
| AF packaged stack + AQ product layer + AS trust path + ablated DECODE (snippet-prefix + gibberish-tail STRICT) — not unlabeled open chat LM · not TAC unlocked | Open chat / mini-AGI |
| Usable howto·cite·long content | L_eff alone as ctx win |
| Eval path = prod ask path | LOOKUP-as-IQ · pack theater |
| AH/BB/BA CTX archives stay | Rewrite AH formal-hctxlift-ctxlift |

SAFE note: SAFE / ADVSAFE false-hit score ≠ answer quality; SAFE = no wrong gold only (anti-FP); pack FH 0 ≠ forever held-out generalization; intent-mismatch LOOKUP = false-hit (floordiv/neg/gcd/lshift/rshift/nand); BA+BB forever PASS with BC-FOREVER FP = PACK THEATER; exact-gold ABSTAIN = product miss; gold-substring / gibberish-tail / span-fallback ≠ generative PROMOTE  
Anti-FP: LOOKUP|PEAK|DECODE|ABSTAIN labeled; never LOOKUP-as-IQ; never peak-as-open-chat; SAFE≠quality; gold-substring≠gen; intent-mismatch LOOKUP = false-hit (BC-FOREVER floordiv/neg/gcd/lshift/rshift/nand → add); exact-gold ABSTAIN = miss (a.clear()); BA-FOREVER pow·mod·max·sort·len FH must stay 0; BB-FOREVER min·xor·absdiff·and·or FH must stay 0; AZ hold div·sub·BIP FH must stay 0; BA+BB PASS with BC FP = PACK THEATER; truncate-to-span≠gen IQ; DECODE gibberish≠content_ok; eval path = prod ask path; generative bar = BC4 only under real new method; no NANOGEN13 = NANOGEN12+rename; no CTX/SMART/FAST clone; no invent Wave BD without lab-book reopen; prefer HOLD/defer over fake PROMOTE

Next: **BC4 H-NANOGEN13** — one real gen method or HOLD/DEFER.
