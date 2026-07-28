# H-NANOGEN9 — gen-defer gate (**DONE** — DEFER)

> Lab: `.local/pesquisa.md` §5 AY3 · Session: `.local/wave-ay/SESSION.md`  
> Parent: [formal-hnanogen8-nanogen8.md](formal-hnanogen8-nanogen8.md) (**DEFER**) · [formal-hnanogen7-nanogen7.md](formal-hnanogen7-nanogen7.md) · [formal-hnanogen6-nanogen6.md](formal-hnanogen6-nanogen6.md) · AY0 stance **defer**  
> Module: `nano_lm/src/nanogen9_ops.py` · Runner: `npm run nano:nanogen9`

## Hypothesis

North-star generative gate under AY0 gen stance: PROMOTE only with a real new train/data/arch method AND true_continue; else DEFER/HOLD. CAPCHECK closed; never NANOGEN9 = NANOGEN8+rename; NANOGEN6·7 HOLD · NANOGEN8 DEFER stand; span-fallback ≠ gen IQ; mini-AGI locked while deferred

## Gate

| Metric | Result | Pass bar |
|--------|-------:|----------|
| Stance | **defer** | AY0 freeze |
| CAPCHECK | **closed** | closed |
| real_new_method | **False** | True for PROMOTE |
| method | **gen-defer** / defer | not NANOGEN8 rename |
| is_rename | **False** | False |
| true_continue_mean (archive) | **4.0** | ≥5.5 + method |
| n_true_continue | **0** | >0 for PROMOTE |
| n_span_fallback (archive) | **3** | ≠ gen credit |
| parent NANOGEN6 / 7 | **0.0** / **0.0** | HOLD stand |
| parent NANOGEN8 DEFER | **True** | True |
| live_modes_ok | **True** | LOOKUP+ABSTAIN labeled |
| Decision | **DEFER** | — |

## Live product smoke (modes still honest)

| Arm | product_mode | modeui |
|-----|--------------|--------|
| LOOKUP | **LOOKUP** | `mode=LOOKUP · wall_ms=0.0000 · n_new=0 · raw=WRAP_LOOKUP` |
| DECODE_PROBE | **ABSTAIN** | `mode=ABSTAIN · wall_ms=390.0171 · n_new=64 · raw=NO_ANSWER` |
| ABSTAIN | **ABSTAIN** | `mode=ABSTAIN · wall_ms=371.4991 · n_new=64 · raw=NO_ANSWER` |

## Finding

1. AY0 froze gen stance as **defer**; CAPCHECK **closed**.  
2. No real new train/data/arch method claimed — **not** NANOGEN8 rename theater.  
3. NANOGEN6·7 HOLD · NANOGEN8 DEFER stand (span-fallback ≠ gen).  
4. Live smoke keeps LOOKUP/ABSTAIN labeled on SHIPAY path.  
5. Decision **DEFER** — generative / mini-AGI claim stays locked.  
6. Wall ~3.8s · threads=14 · workers=14.  
7. Next: **AY4 AY-REAL-EVAL** (product pass; gen claim only if AY3 PROMOTE — here deferred).

## Reproduce

```bash
npm run nano:nanogen9
npm run nano:nanogen8
```

## Artifacts

- Summary: `results/nano-lm/wave-ay/nanogen9_summary.json`  
- Contract: `nano_lm/tests/test_nanogen9.py`

## Claims

| Allowed | Forbidden |
|---------|-----------|
| Honest DEFER/HOLD under AY0 stance | NANOGEN9 = NANOGEN8+rename |
| Cite NANOGEN6·7 HOLD · NANOGEN8 DEFER | Vanity gen unlock / LOOKUP-as-IQ |
| PROMOTE only real method + true_continue≥5.5 | Raise ≤5M w/o CAPCHECK |

SAFE note: SAFE / ADVSAFE false-hit score ≠ answer quality; SAFE = no wrong gold only (anti-FP); pack FH 0 ≠ live intent/adversary coverage; intent-mismatch LOOKUP = false-hit; gold-substring / gibberish-tail / span-fallback ≠ generative PROMOTE  
Anti-FP: LOOKUP|PEAK|DECODE|ABSTAIN labeled; never LOOKUP-as-IQ; never peak-as-open-chat; SAFE≠quality; gold-substring≠gen; intent-mismatch LOOKUP = false-hit (mul/diff/remove/half-known); truncate-to-span≠gen IQ; DECODE gibberish≠content_ok; eval path = prod ask path; pack FH 0 ≠ live intent coverage; generative bar = AY3 only under real new method; no NANOGEN9 = NANOGEN8+rename; no CTX/SMART/FAST clone; no invent Wave AZ without lab-book reopen; prefer HOLD/defer over fake PROMOTE  
Ship lock: AF packaged stack + AQ product layer + AS trust path + ablated DECODE (snippet-prefix + gibberish-tail STRICT) — not unlabeled open chat LM · not TAC unlocked

Next: **AY4 AY-REAL-EVAL** (`npm run nano:ay:real-eval`).
