# H-NANOGEN13 — gen-defer gate (**DONE** — DEFER)

> Lab: `.local/pesquisa.md` §4 · §9 BC4 · Session: `.local/wave-bc/SESSION.md`  
> Parent: [formal-hnanogen12-nanogen12.md](formal-hnanogen12-nanogen12.md) (**DEFER**) · [formal-hnanogen11-nanogen11.md](formal-hnanogen11-nanogen11.md) · BC0 stance **defer**  
> Module: `nano_lm/src/nanogen13_ops.py` · Runner: `npm run nano:nanogen13`

## Hypothesis

North-star generative gate under BC0 gen stance: PROMOTE only with a real new train/data/arch method (M1|M2|M3) AND true_continue; else DEFER/HOLD. CAPCHECK closed; never NANOGEN13 = NANOGEN12+rename; NANOGEN6·7 HOLD · NANOGEN8·9·10·11·12 DEFER stand; span-fallback ≠ gen IQ; mini-AGI locked while deferred

## Gate

| Metric | Result | Pass bar |
|--------|-------:|----------|
| Stance | **defer** | BC0 freeze |
| CAPCHECK | **closed** | closed |
| real_new_method | **False** | True for PROMOTE |
| method | **gen-defer** / defer | not NANOGEN12 rename |
| is_rename | **False** | False |
| true_continue_mean (archive) | **4.0** | ≥5.5 + method |
| n_true_continue | **0** | >0 for PROMOTE |
| n_span_fallback (archive) | **3** | ≠ gen credit |
| parent NANOGEN6 / 7 | **4.0** / **4.0** | HOLD stand |
| parent NANOGEN8·9·10·11·12 DEFER | **True** / **True** / **True** / **True** / **True** | True |
| live_modes_ok | **True** | LOOKUP+ABSTAIN · BC-FOREVER ABSTAIN |
| Decision | **DEFER** | — |

## Live product smoke (modes still honest)

| Arm | product_mode | modeui |
|-----|--------------|--------|
| LOOKUP | **LOOKUP** | `mode=LOOKUP · wall_ms=0.0000 · n_new=0 · raw=WRAP_LOOKUP` |
| DECODE_PROBE | **DECODE** | `mode=DECODE · wall_ms=360.9669 · n_new=64 · raw=WRAP_DECODE` |
| ABSTAIN | **ABSTAIN** | `mode=ABSTAIN · wall_ms=348.2065 · n_new=64 · raw=NO_ANSWER` |
| BC_FOREVER | **ABSTAIN** | `mode=ABSTAIN · wall_ms=0.0000 · n_new=0 · raw=NO_ANSWER` |

## Finding

1. BC0 froze gen stance as **defer**; CAPCHECK **closed**.  
2. No real M1|M2|M3 method claimed — **not** NANOGEN12 rename.  
3. NANOGEN6·7 HOLD · NANOGEN8·9·10·11·12 DEFER stand (span-fallback ≠ gen).  
4. Live smoke keeps LOOKUP/ABSTAIN labeled; BC-FOREVER ABSTAIN.  
5. Decision **DEFER** — generative / mini-AGI claim stays locked.  
6. Wall ~3.8s · threads=12 · workers=8.  
7. Next: **BC5 BC-REAL-EVAL** (gen claim only if BC4 PROMOTE).  

## Reproduce

```bash
npm run nano:nanogen13
npm run nano:test && npm run verify
```

## Artifacts

- Summary: `results/nano-lm/wave-bc/nanogen13_summary.json`  
- Contract: `nano_lm/tests/test_nanogen13.py`

## Claims

| Allowed | Forbidden |
|---------|-----------|
| Honest DEFER/HOLD under BC0 stance | NANOGEN13 = NANOGEN12+rename |
| Cite NANOGEN6·7 HOLD · NANOGEN8·9·10·11·12 DEFER | Vanity gen unlock / LOOKUP-as-IQ |
| PROMOTE only real method + true_continue≥5.5 | Raise ≤5M w/o CAPCHECK |

SAFE note: SAFE / ADVSAFE false-hit score ≠ answer quality; SAFE = no wrong gold only (anti-FP); pack FH 0 ≠ forever held-out generalization; intent-mismatch LOOKUP = false-hit (floordiv/neg/gcd/lshift/rshift/nand); BA+BB forever PASS with BC-FOREVER FP = PACK THEATER; exact-gold ABSTAIN = product miss; gold-substring / gibberish-tail / span-fallback ≠ generative PROMOTE  
Anti-FP: LOOKUP|PEAK|DECODE|ABSTAIN labeled; never LOOKUP-as-IQ; never peak-as-open-chat; SAFE≠quality; gold-substring≠gen; intent-mismatch LOOKUP = false-hit (BC-FOREVER floordiv/neg/gcd/lshift/rshift/nand → add); exact-gold ABSTAIN = miss (a.clear()); BA-FOREVER pow·mod·max·sort·len FH must stay 0; BB-FOREVER min·xor·absdiff·and·or FH must stay 0; AZ hold div·sub·BIP FH must stay 0; BA+BB PASS with BC FP = PACK THEATER; truncate-to-span≠gen IQ; DECODE gibberish≠content_ok; eval path = prod ask path; generative bar = BC4 only under real new method; no NANOGEN13 = NANOGEN12+rename; no CTX/SMART/FAST clone; no invent Wave BD without lab-book reopen; prefer HOLD/defer over fake PROMOTE  
Ship lock: AF packaged stack + AQ product layer + AS trust path + ablated DECODE (snippet-prefix + gibberish-tail STRICT) — not unlabeled open chat LM · not TAC unlocked

Next: **BC5 BC-REAL-EVAL** (`npm run nano:bc:real-eval`).
