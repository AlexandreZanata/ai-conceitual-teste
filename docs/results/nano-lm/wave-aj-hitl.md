# AJ-HITL-10 — Wave AJ final dual-arm verify (**DONE** — PROMOTE)

> Lab: `.local/pesquisa.md` §3 AJ6 · Session: `.local/wave-aj/SESSION.md`  
> Declared stack: GENPEAK · CTXPEAK · SMARTPEAK · FASTPEAK · APPPEAK + SEMWRAP/ASKFAST  
> Module: `nano_lm/src/aj_hitl_ops.py` · Runner: `npm run nano:aj:hitl`

## Hypothesis

Final Cursor **ASK→EVAL→FIX×10 dual-arm** on the frozen **AJ0** held-out pack (≠ AB…AI) passes lookup mean ≥ **7.0** and either gen mean ≥ **5.0** **or** documented **HOLD**, with errors ≤ **3**/arm and anti-FP telemetry (`mode`, `wall_ms`, `n_new`).

## Gate

| Metric | Result | Pass bar |
|--------|-------:|----------|
| LOOKUP mean | **9.0** | ≥ **7.0** |
| LOOKUP errors | **0**/10 | ≤ **3** |
| FALSE_HIT | **0** | must be 0 |
| GENERATE mean | **9.0** | ≥ **5.0** for PROMOTE else **HOLD** |
| gen wall_ms>0 ∧ n_new>0 | **10**/10 | else **KILL** |
| held-out vs AB…AI | **ok** | no question-text overlap |
| FIX count | **0** | logged if any |
| mix | known 3 · howto 5 · longdoc 2 | AJ0 freeze |
| Decision | **PROMOTE** | lookup∧gen≥5 · peak product |

## Frontier EVAL — LOOKUP arm

| Trial | Score | Notes |
|-------|------:|-------|
| AJ-FINAL-LOOKUP-HITL-01…10 | 9 | TRUE_HIT · WRAP_LOOKUP · ≠ generative IQ |

**LOOKUP mean:** 9.0 · **FALSE_HIT:** 0/10

## Frontier EVAL — GENERATE arm (QPFB2+GROUNDED+PEAK)

| Trial | Score | error? | Completion | Notes |
|-------|------:|:------:|------------|-------|
| AJ-FINAL-GEN-HITL-01 | 9 | no | `32` | peak · wall>0 · n_new>0 |
| AJ-FINAL-GEN-HITL-02 | 9 | no | `1` | peak · wall>0 · n_new>0 |
| AJ-FINAL-GEN-HITL-03 | 9 | no | `P2WSH` | peak · wall>0 · n_new>0 |
| AJ-FINAL-GEN-HITL-04 | 9 | no | `collections.deque` | peak · wall>0 · n_new>0 |
| AJ-FINAL-GEN-HITL-05 | 9 | no | `continue` | peak · wall>0 · n_new>0 |
| AJ-FINAL-GEN-HITL-06 | 9 | no | `isinstance` | peak · wall>0 · n_new>0 |
| AJ-FINAL-GEN-HITL-07 | 9 | no | `i32` | peak · wall>0 · n_new>0 |
| AJ-FINAL-GEN-HITL-08 | 9 | no | `field init shorthand` | peak · wall>0 · n_new>0 |
| AJ-FINAL-GEN-HITL-09 | 9 | no | `/wallet/<walletname>/` | peak · wall>0 · n_new>0 |
| AJ-FINAL-GEN-HITL-10 | 9 | no | `Internet Header Length` | peak · wall>0 · n_new>0 |

**GEN mean:** 9.0 · Grounded extractive peak product — **not** open-chat TinyStories IQ

### Cursor EVAL bullets

1. Completions are exact peak golds — not period collapse / mid-open drift.  
2. Every gen trial keeps `wall_ms>0` and `n_new>0`.  
3. Do **not** sell LOOKUP TRUE_HIT as generative IQ; ship remains **AF packaged stack** (scoped peak product).

## Finding

1. Final dual-arm verify holds LOOKUP product quality (mean **9.0**, false-hit **0**).  
2. Generative arm clears gen≥5 at **9.0** via GENPEAK peak stops (beats AI-HITL HOLD gen **4.0**).  
3. Gate closes as **PROMOTE** — still **not** an open-chat / unbounded LM claim.  
4. **Ship claim:** scoped **AF packaged stack** with AJ dual-arm peak verify — LOOKUP ≠ generative IQ.

## Reproduce

```bash
npm run nano:aj:session
npm run nano:aj:hitl
npm run nano:test && npm run verify
```

## Artifacts

- Summary: `results/nano-lm/wave-aj/aj_hitl_summary.json`  
- Trials: `AJ-FINAL-LOOKUP-HITL-01…10` · `AJ-FINAL-GEN-HITL-01…10`  
- Contract: `nano_lm/tests/test_aj_hitl.py`

Next: **AJ7 AJ-REPORT**.
