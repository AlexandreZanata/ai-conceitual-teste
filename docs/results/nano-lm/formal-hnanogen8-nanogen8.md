# H-NANOGEN8 — gen-defer gate (**DONE** — DEFER)

> Lab: `.local/pesquisa.md` §5 AX3 · Session: `.local/wave-ax/SESSION.md`  
> Parent: [formal-hnanogen7-nanogen7.md](formal-hnanogen7-nanogen7.md) (true_continue **0**) · [formal-hnanogen6-nanogen6.md](formal-hnanogen6-nanogen6.md) · AX0 stance **defer**  
> Module: `nano_lm/src/nanogen8_ops.py` · Runner: `npm run nano:nanogen8`

## Hypothesis

North-star generative gate under AX0 gen stance: PROMOTE only with a real new train/data/arch method AND true_continue; else DEFER/HOLD. CAPCHECK closed; never NANOGEN8 = NANOGEN7 TAC rename; span-fallback ≠ gen IQ; mini-AGI locked while deferred

## Gate

| Metric | Result | Pass bar |
|--------|-------:|----------|
| Stance | **defer** | AX0 freeze |
| CAPCHECK | **closed** | closed |
| real_new_method | **False** | True for PROMOTE |
| method | **gen-defer** / defer | not TAC rename |
| is_rename | **False** | False |
| true_continue_mean (archive) | **4.0** | ≥5.5 + method |
| n_true_continue | **0** | >0 for PROMOTE |
| n_span_fallback (archive) | **3** | ≠ gen credit |
| parent NANOGEN6 / 7 | **0.0** / **0.0** | HOLD stand |
| live_modes_ok | **True** | LOOKUP+ABSTAIN labeled |
| Decision | **DEFER** | — |

## Live product smoke (modes still honest)

| Arm | product_mode | modeui |
|-----|--------------|--------|
| LOOKUP | **LOOKUP** | `mode=LOOKUP · wall_ms=0.0000 · n_new=0 · raw=WRAP_LOOKUP` |
| DECODE_PROBE | **ABSTAIN** | `mode=ABSTAIN · wall_ms=327.7146 · n_new=64 · raw=NO_ANSWER` |
| ABSTAIN | **ABSTAIN** | `mode=ABSTAIN · wall_ms=327.6451 · n_new=64 · raw=NO_ANSWER` |

## Finding

1. AX0 froze gen stance as **defer**; CAPCHECK **closed**.  
2. No real new train/data/arch method claimed — **not** NANOGEN7 TAC rename theater.  
3. Archived NANOGEN6·7 true_continue remain **0** (span-fallback ≠ gen).  
4. Live smoke keeps LOOKUP/ABSTAIN labeled on product path.  
5. Decision **DEFER** — generative / mini-AGI claim stays locked.  
6. Wall ~3.9s · threads=14 · workers=14.  
7. Next: **AX4 AX-REAL-EVAL** (product pass; gen claim only if AX3 PROMOTE — here deferred).

## Reproduce

```bash
npm run nano:nanogen8
npm run nano:nanogen7
```

## Artifacts

- Summary: `results/nano-lm/wave-ax/nanogen8_summary.json`  
- Contract: `nano_lm/tests/test_nanogen8.py`

## Claims

| Allowed | Forbidden |
|---------|-----------|
| Honest DEFER/HOLD under AX0 stance | NANOGEN8 = NANOGEN7+rename |
| Cite NANOGEN6·7 HOLD | Vanity gen unlock / LOOKUP-as-IQ |
| PROMOTE only real method + true_continue≥5.5 | Raise ≤5M w/o CAPCHECK |

SAFE note: SAFE / ADVSAFE false-hit score ≠ answer quality; SAFE = no wrong gold only (anti-FP); pack/pressure-para ≠ hard natural coverage; gold-substring / gibberish-tail / span-fallback ≠ generative PROMOTE  
Anti-FP: LOOKUP|PEAK|DECODE|ABSTAIN labeled; never LOOKUP-as-IQ; never peak-as-open-chat; SAFE≠quality; gold-substring≠gen; truncate-to-span≠gen IQ; DECODE gibberish≠content_ok; eval path = prod ask path; pack-para ≠ hard natural coverage; generative bar = AX3 only under real new method; no NANOGEN8 = NANOGEN7+rename; no CTX/SMART/FAST clone; no invent Wave AY without lab-book reopen; prefer HOLD/defer over fake PROMOTE  
Ship lock: AF packaged stack + AQ product layer + AS trust path + ablated DECODE (snippet-prefix + gibberish-tail STRICT) — not unlabeled open chat LM · not TAC unlocked

Next: **AX4 AX-REAL-EVAL** (`npm run nano:ax:real-eval`).
