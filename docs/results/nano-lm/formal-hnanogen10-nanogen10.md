# H-NANOGEN10 — gen-defer gate (**DONE** — DEFER)

> Lab: `.local/pesquisa.md` §5 AZ3 · Session: `.local/wave-az/SESSION.md`  
> Parent: [formal-hnanogen9-nanogen9.md](formal-hnanogen9-nanogen9.md) (**DEFER**) · [formal-hnanogen8-nanogen8.md](formal-hnanogen8-nanogen8.md) (**DEFER**) · [formal-hnanogen7-nanogen7.md](formal-hnanogen7-nanogen7.md) · [formal-hnanogen6-nanogen6.md](formal-hnanogen6-nanogen6.md) · AZ0 stance **defer**  
> Module: `nano_lm/src/nanogen10_ops.py` · Runner: `npm run nano:nanogen10`

## Hypothesis

North-star generative gate under AZ0 gen stance: PROMOTE only with a real new train/data/arch method AND true_continue; else DEFER/HOLD. CAPCHECK closed; never NANOGEN10 = NANOGEN9+rename; NANOGEN6·7 HOLD · NANOGEN8·9 DEFER stand; span-fallback ≠ gen IQ; mini-AGI locked while deferred

## Gate

| Metric | Result | Pass bar |
|--------|-------:|----------|
| Stance | **defer** | AZ0 freeze |
| CAPCHECK | **closed** | closed |
| real_new_method | **False** | True for PROMOTE |
| method | **gen-defer** / defer | not NANOGEN9 rename |
| is_rename | **False** | False |
| true_continue_mean (archive) | **4.0** | ≥5.5 + method |
| n_true_continue | **0** | >0 for PROMOTE |
| n_span_fallback (archive) | **3** | ≠ gen credit |
| parent NANOGEN6 / 7 | **0.0** / **0.0** | HOLD stand |
| parent NANOGEN8 DEFER | **True** | True |
| parent NANOGEN9 DEFER | **True** | True |
| live_modes_ok | **True** | LOOKUP+ABSTAIN labeled |
| Decision | **DEFER** | — |

## Live product smoke (modes still honest)

| Arm | product_mode | modeui |
|-----|--------------|--------|
| LOOKUP | **LOOKUP** | `mode=LOOKUP · wall_ms=0.0000 · n_new=0 · raw=WRAP_LOOKUP` |
| DECODE_PROBE | **ABSTAIN** | `mode=ABSTAIN · wall_ms=346.3108 · n_new=64 · raw=NO_ANSWER` |
| ABSTAIN | **ABSTAIN** | `mode=ABSTAIN · wall_ms=346.3666 · n_new=64 · raw=NO_ANSWER` |

## Finding

1. AZ0 froze gen stance as **defer**; CAPCHECK **closed**.  
2. No real new train/data/arch method claimed — **not** NANOGEN9 rename theater.  
3. NANOGEN6·7 HOLD · NANOGEN8·9 DEFER stand (span-fallback ≠ gen).  
4. Live smoke keeps LOOKUP/ABSTAIN labeled on SHIPAZ path.  
5. Decision **DEFER** — generative / mini-AGI claim stays locked.  
6. Wall ~3.9s · threads=14 · workers=14.  
7. Next: **AZ4 AZ-REAL-EVAL** (product pass; gen claim only if AZ3 PROMOTE — here deferred).

## Reproduce

```bash
npm run nano:nanogen10
npm run nano:nanogen9
```

## Artifacts

- Summary: `results/nano-lm/wave-az/nanogen10_summary.json`  
- Contract: `nano_lm/tests/test_nanogen10.py`

## Claims

| Allowed | Forbidden |
|---------|-----------|
| Honest DEFER/HOLD under AZ0 stance | NANOGEN10 = NANOGEN9+rename |
| Cite NANOGEN6·7 HOLD · NANOGEN8·9 DEFER | Vanity gen unlock / LOOKUP-as-IQ |
| PROMOTE only real method + true_continue≥5.5 | Raise ≤5M w/o CAPCHECK |

SAFE note: SAFE / ADVSAFE false-hit score ≠ answer quality; SAFE = no wrong gold only (anti-FP); named-class FH 0 ≠ held-out generalization; intent-mismatch LOOKUP = false-hit; exact-gold ABSTAIN = product miss; gold-substring / gibberish-tail / span-fallback ≠ generative PROMOTE  
Anti-FP: LOOKUP|PEAK|DECODE|ABSTAIN labeled; never LOOKUP-as-IQ; never peak-as-open-chat; SAFE≠quality; gold-substring≠gen; intent-mismatch LOOKUP = false-hit (div/sub/wrong-slot held-out); exact-gold ABSTAIN = miss (a.clear()); truncate-to-span≠gen IQ; DECODE gibberish≠content_ok; eval path = prod ask path; pack/named FH 0 ≠ held-out coverage; generative bar = AZ3 only under real new method; no NANOGEN10 = NANOGEN9+rename; no CTX/SMART/FAST clone; no invent Wave BA without lab-book reopen; prefer HOLD/defer over fake PROMOTE  
Ship lock: AF packaged stack + AQ product layer + AS trust path + ablated DECODE (snippet-prefix + gibberish-tail STRICT) — not unlabeled open chat LM · not TAC unlocked

Next: **AZ4 AZ-REAL-EVAL** (`npm run nano:az:real-eval`).
