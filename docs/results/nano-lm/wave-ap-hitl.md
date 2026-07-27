# AP-HITL-10 — Wave AP final dual-arm verify (**DONE** — PROMOTE)

> Lab: `.local/pesquisa.md` §3 AP6 · Session: `.local/wave-ap/SESSION.md`  
> Declared stack: GENBASE · CTXBASE · SMARTBASE · FASTBASE · APPBASE + SEMWRAP/ASKFAST  
> Module: `nano_lm/src/ap_hitl_ops.py` · Runner: `npm run nano:ap:hitl`

## Hypothesis

Final Cursor **ASK→EVAL→FIX×10 dual-arm** on the frozen **AP0** held-out pack (≠ AB…AO) passes lookup mean ≥ **7.0** and either gen mean ≥ **5.0** **or** documented **HOLD**, with errors ≤ **3**/arm and anti-FP telemetry (`mode`, `wall_ms`, `n_new`).

## Gate

| Metric | Result | Pass bar |
|--------|-------:|----------|
| LOOKUP mean | **9.0** | ≥ **7.0** |
| LOOKUP errors | **0**/10 | ≤ **3** |
| FALSE_HIT | **0** | must be 0 |
| GENERATE mean | **9.0** | ≥ **5.0** for PROMOTE else **HOLD** |
| gen wall_ms>0 ∧ n_new>0 | **10**/10 | else **KILL** |
| held-out vs AB…AO | **ok** | no question-text overlap |
| FIX count | **0** | logged if any |
| mix | known 3 · howto 5 · longdoc 2 | AP0 freeze |
| Decision | **PROMOTE** | lookup∧gen≥5 · peak product |

## Frontier EVAL — LOOKUP arm

| Trial | Score | Notes |
|-------|------:|-------|
| AP-FINAL-LOOKUP-HITL-01…10 | 9 | TRUE_HIT · WRAP_LOOKUP · ≠ generative IQ |

**LOOKUP mean:** 9.0 · **FALSE_HIT:** 0/10

## Frontier EVAL — GENERATE arm (QPFB2+GROUNDED+GENBASE_PEAK)

| Trial | Score | error? | Completion | Notes |
|-------|------:|:------:|------------|-------|
| AP-FINAL-GEN-HITL-01 | 9 | no | `CS = ENT / 32` | peak · wall>0 · n_new>0 |
| AP-FINAL-GEN-HITL-02 | 9 | no | `0x00000000` | peak · wall>0 · n_new>0 |
| AP-FINAL-GEN-HITL-03 | 9 | no | `P2WPKH` | peak · wall>0 · n_new>0 |
| AP-FINAL-GEN-HITL-04 | 9 | no | `a.append(x)` | peak · wall>0 · n_new>0 |
| AP-FINAL-GEN-HITL-05 | 9 | no | `pass` | peak · wall>0 · n_new>0 |
| AP-FINAL-GEN-HITL-06 | 9 | no | `issubclass` | peak · wall>0 · n_new>0 |
| AP-FINAL-GEN-HITL-07 | 9 | no | `isize or usize` | peak · wall>0 · n_new>0 |
| AP-FINAL-GEN-HITL-08 | 9 | no | `..` | peak · wall>0 · n_new>0 |
| AP-FINAL-GEN-HITL-09 | 9 | no | `GET /rest/tx/<TX-HASH>.<bin\|hex\|json>` | peak · wall>0 · n_new>0 |
| AP-FINAL-GEN-HITL-10 | 9 | no | `8` | peak · wall>0 · n_new>0 |

**GEN mean:** 9.0 · Grounded extractive peak product — **not** open-chat TinyStories IQ (GENBASE HOLD still stands for ablated true-gen)

### Cursor EVAL bullets

1. Completions are exact peak golds — including `..` (not period collapse) and BIP/REST/RFC spans.  
2. Every gen trial keeps `wall_ms>0` and `n_new>0` (14 CPU threads, leave-2-cores).  
3. Do **not** sell LOOKUP TRUE_HIT as generative IQ; ship remains **AF packaged stack** (scoped peak product).

## Finding

1. Final dual-arm verify holds LOOKUP product quality (mean **9.0**, false-hit **0**).  
2. Generative arm clears gen≥5 at **9.0** via GENBASE peak stops.  
3. Gate closes as **PROMOTE** — still **not** an open-chat / unbounded LM claim.  
4. **Ship claim:** scoped **AF packaged stack** with AP dual-arm base verify — LOOKUP ≠ generative IQ.

## Reproduce

```bash
npm run nano:ap:session
npm run nano:ap:hitl
npm run nano:test && npm run verify
```

## Artifacts

- Summary: `results/nano-lm/wave-ap/ap_hitl_summary.json`  
- Trials: `AP-FINAL-LOOKUP-HITL-01…10` · `AP-FINAL-GEN-HITL-01…10`  
- Contract: `nano_lm/tests/test_ap_hitl.py`

Next: **AP7 AP-REPORT** — public summary + paper-lab. Do **not** invent Wave AQ.
