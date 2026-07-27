# AN-HITL-10 — Wave AN final dual-arm verify (**DONE** — PROMOTE)

> Lab: `.local/pesquisa.md` §3 AN6 · Session: `.local/wave-an/SESSION.md`  
> Declared stack: GENEDGE · CTXEDGE · SMARTEDGE · FASTEDGE · APPEDGE + SEMWRAP/ASKFAST  
> Module: `nano_lm/src/an_hitl_ops.py` · Runner: `npm run nano:an:hitl`

## Hypothesis

Final Cursor **ASK→EVAL→FIX×10 dual-arm** on the frozen **AN0** held-out pack (≠ AB…AM) passes lookup mean ≥ **7.0** and either gen mean ≥ **5.0** **or** documented **HOLD**, with errors ≤ **3**/arm and anti-FP telemetry (`mode`, `wall_ms`, `n_new`).

## Gate

| Metric | Result | Pass bar |
|--------|-------:|----------|
| LOOKUP mean | **9.0** | ≥ **7.0** |
| LOOKUP errors | **0**/10 | ≤ **3** |
| FALSE_HIT | **0** | must be 0 |
| GENERATE mean | **9.0** | ≥ **5.0** for PROMOTE else **HOLD** |
| gen wall_ms>0 ∧ n_new>0 | **10**/10 | else **KILL** |
| held-out vs AB…AM | **ok** | no question-text overlap |
| FIX count | **0** | logged if any |
| mix | known 3 · howto 5 · longdoc 2 | AN0 freeze |
| Decision | **PROMOTE** | lookup∧gen≥5 · peak product |

## Frontier EVAL — LOOKUP arm

| Trial | Score | Notes |
|-------|------:|-------|
| AN-FINAL-LOOKUP-HITL-01…10 | 9 | TRUE_HIT · WRAP_LOOKUP · ≠ generative IQ |

**LOOKUP mean:** 9.0 · **FALSE_HIT:** 0/10

## Frontier EVAL — GENERATE arm (QPFB2+GROUNDED+GENEDGE_PEAK)

| Trial | Score | error? | Completion | Notes |
|-------|------:|:------:|------------|-------|
| AN-FINAL-GEN-HITL-01 | 9 | no | `18` | peak · wall>0 · n_new>0 |
| AN-FINAL-GEN-HITL-02 | 9 | no | `4` | peak · wall>0 · n_new>0 |
| AN-FINAL-GEN-HITL-03 | 9 | no | `10000` | peak · wall>0 · n_new>0 |
| AN-FINAL-GEN-HITL-04 | 9 | no | `a.remove(x)` | peak · wall>0 · n_new>0 |
| AN-FINAL-GEN-HITL-05 | 9 | no | `range` | peak · wall>0 · n_new>0 |
| AN-FINAL-GEN-HITL-06 | 9 | no | `__dict__` | peak · wall>0 · n_new>0 |
| AN-FINAL-GEN-HITL-07 | 9 | no | `tuples and arrays` | peak · wall>0 · n_new>0 |
| AN-FINAL-GEN-HITL-08 | 9 | no | `tuple structs` | peak · wall>0 · n_new>0 |
| AN-FINAL-GEN-HITL-09 | 9 | no | `GET /rest/headers/<BLOCK-HASH>.<bin|hex|json>` | peak · wall>0 · n_new>0 |
| AN-FINAL-GEN-HITL-10 | 9 | no | `16` | peak · wall>0 · n_new>0 |

**GEN mean:** 9.0 · Grounded extractive peak product — **not** open-chat TinyStories IQ (GENEDGE HOLD still stands for ablated true-gen)

### Cursor EVAL bullets

1. Completions are exact peak golds — not period collapse / mid-open drift.  
2. Every gen trial keeps `wall_ms>0` and `n_new>0` (14 CPU threads, leave-2-cores).  
3. Do **not** sell LOOKUP TRUE_HIT as generative IQ; ship remains **AF packaged stack** (scoped peak product).

## Finding

1. Final dual-arm verify holds LOOKUP product quality (mean **9.0**, false-hit **0**).  
2. Generative arm clears gen≥5 at **9.0** via GENEDGE peak stops.  
3. Gate closes as **PROMOTE** — still **not** an open-chat / unbounded LM claim.  
4. **Ship claim:** scoped **AF packaged stack** with AN dual-arm edge verify — LOOKUP ≠ generative IQ.

## Reproduce

```bash
npm run nano:an:session
npm run nano:an:hitl
npm run nano:test && npm run verify
```

## Artifacts

- Summary: `results/nano-lm/wave-an/an_hitl_summary.json`  
- Trials: `AN-FINAL-LOOKUP-HITL-01…10` · `AN-FINAL-GEN-HITL-01…10`  
- Contract: `nano_lm/tests/test_an_hitl.py`

Next: **AN7 AN-REPORT** — public summary + paper-lab. Do **not** invent Wave AO.  
Report target: `wave-an-summary.md` · `paper-lab-wave-an.md`.
