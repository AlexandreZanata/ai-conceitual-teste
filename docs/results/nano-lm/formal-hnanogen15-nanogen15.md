# H-NANOGEN15 — gen-defer-once gate (**DONE** — DEFER)

> Lab: `.local/pesquisa.md` §4 · §9 BE5 · Session: `.local/wave-be/SESSION.md`  
> Parent: [formal-hnanogen14-nanogen14.md](formal-hnanogen14-nanogen14.md) (**DEFER**) · BE0 stance **defer**  
> Module: `nano_lm/src/nanogen15_ops.py` · Runner: `npm run nano:nanogen15`

## Hypothesis

North-star generative gate under BE0 gen stance: PROMOTE only with a real new train/data/arch method (M1|M2|M3) AND true_continue; else DEFER once (stop rule). CAPCHECK closed; never NANOGEN15 = NANOGEN14+rename; NANOGEN6·7 HOLD · NANOGEN8…14 DEFER stand; span-fallback ≠ gen IQ; mini-AGI locked while deferred

## Gate

| Metric | Result | Pass bar |
|--------|-------:|----------|
| Stance | **defer** | BE0 freeze |
| CAPCHECK | **closed** | closed |
| real_new_method | **False** | True for PROMOTE |
| method | **gen-defer-once** / defer | not NANOGEN14 rename |
| is_rename | **False** | False |
| defer_once_stop_rule | **True** | True |
| true_continue_mean (archive) | **4.0** | ≥5.5 + method |
| n_true_continue | **0** | >0 for PROMOTE |
| n_span_fallback (archive) | **3** | ≠ gen credit |
| parent NANOGEN6 / 7 | **4.0** / **4.0** | HOLD stand |
| parent NANOGEN8…14 DEFER | **True** / **True** / **True** / **True** / **True** / **True** / **True** | True |
| live_modes_ok | **True** | LOOKUP+ABSTAIN · BD/BE-FOREVER ABSTAIN |
| Decision | **DEFER** | — |

## Live product smoke (modes still honest)

| Arm | product_mode | modeui |
|-----|--------------|--------|
| LOOKUP | **LOOKUP** | `mode=LOOKUP · wall_ms=0.0000 · n_new=0 · raw=WRAP_LOOKUP` |
| DECODE_PROBE | **DECODE** | `mode=DECODE · wall_ms=327.1197 · n_new=64 · raw=WRAP_DECODE` |
| ABSTAIN | **ABSTAIN** | `mode=ABSTAIN · wall_ms=338.5734 · n_new=64 · raw=NO_ANSWER` |
| BD_FOREVER | **ABSTAIN** | `mode=ABSTAIN · wall_ms=0.0000 · n_new=0 · raw=NO_ANSWER` |
| BE_FOREVER | **ABSTAIN** | `mode=ABSTAIN · wall_ms=0.0000 · n_new=0 · raw=NO_ANSWER` |

## Finding

1. BE0 froze gen stance as **defer**; CAPCHECK **closed**.  
2. No real M1|M2|M3 method claimed — **not** NANOGEN14 rename.  
3. NANOGEN6·7 HOLD · NANOGEN8…14 DEFER stand (span-fallback ≠ gen).  
4. Live smoke keeps LOOKUP/ABSTAIN labeled; BD/BE-FOREVER ABSTAIN.  
5. Decision **DEFER** — generative / mini-AGI claim stays locked (DEFER once stop rule).  
6. Wall ~3.8s · threads=10 · workers=6 (`cpus-6`).  
7. Next: **BE6 BE-REAL-EVAL** (gen claim only if BE5 PROMOTE).  

## Reproduce

```bash
npm run nano:nanogen15
npm run nano:test && npm run verify
```

## Artifacts

- Summary: `results/nano-lm/wave-be/nanogen15_summary.json`  
- Contract: `nano_lm/tests/test_nanogen15.py`

## Claims

| Allowed | Forbidden |
|---------|-----------|
| Honest DEFER/HOLD under BE0 stance | NANOGEN15 = NANOGEN14+rename |
| Cite NANOGEN6·7 HOLD · NANOGEN8…14 DEFER | Vanity gen unlock / LOOKUP-as-IQ |
| PROMOTE only real method + true_continue≥5.5 | Raise ≤5M w/o CAPCHECK |

SAFE note: SAFE / ADVSAFE false-hit score ≠ answer quality; SAFE = no wrong gold only (anti-FP); pack FH 0 ≠ forever held-out generalization; type/coercion wrong-bank LOOKUP = false-hit (str→int→def add); BA…BD forever PASS with BE-FOREVER FP = PACK THEATER; exact-gold ABSTAIN = product miss; gold-substring / gibberish-tail / span-fallback ≠ generative PROMOTE  
Anti-FP: LOOKUP|PEAK|DECODE|ABSTAIN labeled; never LOOKUP-as-IQ; never peak-as-open-chat; SAFE≠quality; gold-substring≠gen; type/coercion LOOKUP = false-hit (BE-FOREVER str→int→add); exact-gold ABSTAIN = miss (a.clear()); BA-FOREVER pow·mod·max·sort·len FH must stay 0; BB-FOREVER min·xor·absdiff·and·or FH must stay 0; BC-FOREVER floordiv·neg·gcd·lshift·rshift·nand FH must stay 0; BD-FOREVER reverse≠f-string · mul≠add FH must stay 0; AZ hold div·sub·BIP FH must stay 0; BA…BD PASS with BE FP = PACK THEATER; truncate-to-span≠gen IQ; DECODE gibberish≠content_ok; eval path = prod ask path; generative bar = BE5 only under real new method; no NANOGEN15 = NANOGEN14+rename; no CTX/SMART/FAST clone; no invent Wave BF without lab-book reopen; prefer compositional gate over bank stuffing; prefer HOLD/defer over fake PROMOTE  
Ship lock: AF packaged stack + AQ product layer + AS trust path + ablated DECODE (snippet-prefix + gibberish-tail STRICT) — not unlabeled open chat LM · not TAC unlocked

Next: **BE6 BE-REAL-EVAL** (`npm run nano:be:real-eval`).
