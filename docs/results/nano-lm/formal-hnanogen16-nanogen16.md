# H-NANOGEN16 — gen-SKIP stop-rule gate (**DONE** — SKIP)

> Lab: `.local/pesquisa.md` §5 · §9 BF5 · Session: `.local/wave-bf/SESSION.md`  
> Parent: [formal-hnanogen15-nanogen15.md](formal-hnanogen15-nanogen15.md) (**DEFER**) · BF0 stance **skip**  
> Module: `nano_lm/src/nanogen16_ops.py` · Runner: `npm run nano:nanogen16`

## Hypothesis

North-star generative gate under BF0 gen stance: PROMOTE only with a written M1|M2|M3 method plan AND true_continue; else SKIP stage (stop rule — not empty DEFER letter). CAPCHECK closed; never NANOGEN16 = NANOGEN15+rename; NANOGEN6·7 HOLD · NANOGEN8…15 DEFER stand; span-fallback ≠ gen IQ; mini-AGI locked while skipped

## Gate

| Metric | Result | Pass bar |
|--------|-------:|----------|
| Stance | **skip** | BF0 freeze |
| CAPCHECK | **closed** | closed |
| method_plan_attached | **False** | True for PROMOTE |
| real_new_method | **False** | True for PROMOTE |
| method | **gen-skip-no-plan** / skip | not NANOGEN15 rename |
| is_rename | **False** | False |
| skip_gen_stop_rule | **True** | True |
| empty_defer_letter | **False** | False |
| true_continue_mean (archive) | **4.0** | ≥5.5 + plan |
| n_true_continue | **0** | >0 for PROMOTE |
| n_span_fallback (archive) | **3** | ≠ gen credit |
| parent NANOGEN6 / 7 | **4.0** / **4.0** | HOLD stand |
| parent NANOGEN8…15 DEFER | **True** / **True** / **True** / **True** / **True** / **True** / **True** / **True** | True |
| live_modes_ok | **True** | LOOKUP+ABSTAIN · BD/BE/BF-FOREVER ABSTAIN |
| Decision | **SKIP** | — |

## Live product smoke (modes still honest)

| Arm | product_mode | modeui |
|-----|--------------|--------|
| LOOKUP | **LOOKUP** | `mode=LOOKUP · wall_ms=0.0000 · n_new=0 · raw=WRAP_LOOKUP` |
| DECODE_PROBE | **DECODE** | `mode=DECODE · wall_ms=329.9223 · n_new=64 · raw=WRAP_DECODE` |
| ABSTAIN | **ABSTAIN** | `mode=ABSTAIN · wall_ms=346.2083 · n_new=64 · raw=NO_ANSWER` |
| BD_FOREVER | **ABSTAIN** | `mode=ABSTAIN · wall_ms=0.0000 · n_new=0 · raw=NO_ANSWER` |
| BE_FOREVER | **ABSTAIN** | `mode=ABSTAIN · wall_ms=0.0000 · n_new=0 · raw=NO_ANSWER` |
| BF_FOREVER | **ABSTAIN** | `mode=ABSTAIN · wall_ms=0.0000 · n_new=0 · raw=NO_ANSWER` |

## Finding

1. BF0 froze gen stance as **skip**; CAPCHECK **closed**; no written M1|M2|M3 plan.  
2. H-NANOGEN15 already **DEFER once** — stop rule forbids empty NANOGEN16 DEFER letter → **SKIP stage**.  
3. Not NANOGEN15/14/…/6 rename. NANOGEN6·7 HOLD · NANOGEN8…15 DEFER stand (span-fallback ≠ gen).  
4. Live smoke keeps LOOKUP/ABSTAIN labeled; BD/BE/BF-FOREVER ABSTAIN.  
5. Decision **SKIP** — generative / mini-AGI claim stays locked (SKIP stop rule).  
6. Wall ~3.8s · threads=10 · workers=6 (`cpus-6`).  
7. Next: **BF6 BF-REAL-EVAL** (gen claim only if BF5 PROMOTE).  

## Reproduce

```bash
npm run nano:nanogen16
npm run nano:test && npm run verify
```

## Artifacts

- Summary: `results/nano-lm/wave-bf/nanogen16_summary.json`  
- Contract: `nano_lm/tests/test_nanogen16.py`

## Claims

| Allowed | Forbidden |
|---------|-----------|
| Honest SKIP under BF0 stance | Empty DEFER letter / NANOGEN15+rename |
| Cite NANOGEN6·7 HOLD · NANOGEN8…15 DEFER | Vanity gen unlock / LOOKUP-as-IQ |
| PROMOTE only written plan + true_continue≥5.5 | Raise ≤5M w/o CAPCHECK |

SAFE note: SAFE / ADVSAFE false-hit score ≠ answer quality; SAFE = no wrong gold only (anti-FP); pack FH 0 ≠ forever held-out generalization; predicate/boolean wrong-bank LOOKUP = false-hit (even→def add); BA…BE forever PASS with BF-FOREVER FP = PACK THEATER; exact-gold ABSTAIN = product miss; gold-substring / gibberish-tail / span-fallback ≠ generative PROMOTE  
Anti-FP: LOOKUP|PEAK|DECODE|ABSTAIN labeled; never LOOKUP-as-IQ; never peak-as-open-chat; SAFE≠quality; gold-substring≠gen; predicate/boolean LOOKUP = false-hit (BF-FOREVER even→add); type/coercion LOOKUP = false-hit (BE-FOREVER str→int→add); exact-gold ABSTAIN = miss (a.clear()); BA-FOREVER pow·mod·max·sort·len FH must stay 0; BB-FOREVER min·xor·absdiff·and·or FH must stay 0; BC-FOREVER floordiv·neg·gcd·lshift·rshift·nand FH must stay 0; BD-FOREVER reverse≠f-string · mul≠add FH must stay 0; BE-FOREVER str→int / type-coercion FH must stay 0; AZ hold div·sub·BIP FH must stay 0; BA…BE PASS with BF FP = PACK THEATER; truncate-to-span≠gen IQ; DECODE gibberish≠content_ok; eval path = prod ask path; generative bar = BF5 only under written method plan; no NANOGEN16 without M1|M2|M3 plan; no CTX/SMART/FAST clone; no invent Wave BG without lab-book reopen; prefer predicate/schema gate over bank stuffing; prefer HOLD/SKIP over fake PROMOTE  
Ship lock: AF packaged stack + AQ product layer + AS trust path + ablated DECODE (snippet-prefix + gibberish-tail STRICT) — not unlabeled open chat LM · not TAC unlocked

Next: **BF6 BF-REAL-EVAL** (`npm run nano:bf:real-eval`).
