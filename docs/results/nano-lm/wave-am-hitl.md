# AM-HITL-10 — Wave AM final dual-arm verify (**DONE** — PROMOTE)

> Lab: `.local/pesquisa.md` §3 AM6 · Session: `.local/wave-am/SESSION.md`  
> Declared stack: GENTRUTH · CTXNEXT · SMARTNEXT · FASTNEXT · APPNEXT + SEMWRAP/ASKFAST  
> Module: `nano_lm/src/am_hitl_ops.py` · Runner: `npm run nano:am:hitl`

## Hypothesis

Final Cursor **ASK→EVAL→FIX×10 dual-arm** on the frozen **AM0** held-out pack (≠ AB…AL) passes lookup mean ≥ **7.0** and either gen mean ≥ **5.0** **or** documented **HOLD**, with errors ≤ **3**/arm and anti-FP telemetry (`mode`, `wall_ms`, `n_new`).

## Gate

| Metric | Result | Pass bar |
|--------|-------:|----------|
| LOOKUP mean | **9.0** | ≥ **7.0** |
| LOOKUP errors | **0**/10 | ≤ **3** |
| FALSE_HIT | **0** | must be 0 |
| GENERATE mean | **9.0** | ≥ **5.0** for PROMOTE else **HOLD** |
| gen wall_ms>0 ∧ n_new>0 | **10**/10 | else **KILL** |
| held-out vs AB…AL | **ok** | no question-text overlap |
| FIX count | **0** | logged if any |
| mix | known 3 · howto 5 · longdoc 2 | AM0 freeze |
| Decision | **PROMOTE** | lookup∧gen≥5 · peak product |

## Frontier EVAL — LOOKUP arm

| Trial | Score | Notes |
|-------|------:|-------|
| AM-FINAL-LOOKUP-HITL-01…10 | 9 | TRUE_HIT · WRAP_LOOKUP · ≠ generative IQ |

**LOOKUP mean:** 9.0 · **FALSE_HIT:** 0/10

## Frontier EVAL — GENERATE arm (QPFB2+GROUNDED+GENTRUTH_PEAK)

| Trial | Score | error? | Completion | Notes |
|-------|------:|:------:|------------|-------|
| AM-FINAL-GEN-HITL-01 | 9 | no | `15` | peak · wall>0 · n_new>0 |
| AM-FINAL-GEN-HITL-02 | 9 | no | `33` | peak · wall>0 · n_new>0 |
| AM-FINAL-GEN-HITL-03 | 9 | no | `2` | peak · wall>0 · n_new>0 |
| AM-FINAL-GEN-HITL-04 | 9 | no | `a.index(x)` | peak · wall>0 · n_new>0 |
| AM-FINAL-GEN-HITL-05 | 9 | no | `else` | peak · wall>0 · n_new>0 |
| AM-FINAL-GEN-HITL-06 | 9 | no | `setattr` | peak · wall>0 · n_new>0 |
| AM-FINAL-GEN-HITL-07 | 9 | no | `4` | peak · wall>0 · n_new>0 |
| AM-FINAL-GEN-HITL-08 | 9 | no | `fields` | peak · wall>0 · n_new>0 |
| AM-FINAL-GEN-HITL-09 | 9 | no | `GET /rest/mempool/contents.json` | peak · wall>0 · n_new>0 |
| AM-FINAL-GEN-HITL-10 | 9 | no | `4` | peak · wall>0 · n_new>0 |

**GEN mean:** 9.0 · Grounded extractive peak product — **not** open-chat TinyStories IQ (GENTRUTH HOLD still stands for ablated true-gen)

### Cursor EVAL bullets

1. Completions are exact peak golds — not period collapse / mid-open drift.  
2. Every gen trial keeps `wall_ms>0` and `n_new>0`.  
3. Do **not** sell LOOKUP TRUE_HIT as generative IQ; ship remains **AF packaged stack** (scoped peak product).

## Finding

1. Final dual-arm verify holds LOOKUP product quality (mean **9.0**, false-hit **0**).  
2. Generative arm clears gen≥5 at **9.0** via GENTRUTH peak stops.  
3. Gate closes as **PROMOTE** — still **not** an open-chat / unbounded LM claim.  
4. **Ship claim:** scoped **AF packaged stack** with AM dual-arm next verify — LOOKUP ≠ generative IQ.

## Reproduce

```bash
npm run nano:am:session
npm run nano:am:hitl
npm run nano:test && npm run verify
```

## Artifacts

- Summary: `results/nano-lm/wave-am/am_hitl_summary.json`  
- Trials: `AM-FINAL-LOOKUP-HITL-01…10` · `AM-FINAL-GEN-HITL-01…10`  
- Contract: `nano_lm/tests/test_am_hitl.py`

Next: **AM7 AM-REPORT** — public summary + paper-lab.
