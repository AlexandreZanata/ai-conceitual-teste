# AH-HITL-10 — Wave AH final dual-arm verify (**DONE** — HOLD)

> Lab: `.local/pesquisa.md` §5 AH6 · Session: `.local/wave-ah/SESSION.md`  
> Declared stack: GENLIFT · CTXLIFT · SMARTLIFT · FASTLIFT · APPLIFT + SEMWRAP/ASKFAST  
> Module: `nano_lm/src/ah_hitl_ops.py` · Runner: `npm run nano:ah:hitl`

## Hypothesis

Final Cursor **ASK→EVAL→FIX×10 dual-arm** on the frozen **AH0** held-out pack (≠ AB…AG) passes lookup mean ≥ **7.0** and either gen mean ≥ **5.0** **or** documented **HOLD**, with errors ≤ **3**/arm and anti-FP telemetry (`mode`, `wall_ms`, `n_new`).

## Gate

| Metric | Result | Pass bar |
|--------|-------:|----------|
| LOOKUP mean | **9.0** | ≥ **7.0** |
| LOOKUP errors | **0**/10 | ≤ **3** |
| FALSE_HIT | **0** | must be 0 |
| GENERATE mean | **1.0** | ≥ **5.0** for PROMOTE else **HOLD** |
| gen wall_ms>0 ∧ n_new>0 | **10**/10 | else **KILL** |
| held-out vs AB…AG | **ok** | no question-text overlap |
| FIX count | **0** | logged if any |
| mix | known 3 · howto 5 · longdoc 2 | AH0 freeze |
| Decision | **HOLD** | lookup ok; gen &lt; 5 (documented) |

## Frontier EVAL — LOOKUP arm

| Trial | Score | Notes |
|-------|------:|-------|
| AH-FINAL-LOOKUP-HITL-01…10 | 9 | TRUE_HIT · WRAP_LOOKUP · ≠ generative IQ |

**LOOKUP mean:** 9.0 · **FALSE_HIT:** 0/10

## Frontier EVAL — GENERATE arm

| Trial | Score | error? | Notes |
|-------|------:|:------:|-------|
| AH-FINAL-GEN-HITL-01…10 | 1 | yes | QT+EARLY wrap=False · period collapse · wall_ms&gt;0 |

**GEN mean:** 1.0 · Peak smarter gen earlier in wave: GENLIFT / SMARTLIFT open mid **4.0** (still &lt;5) · not open chat IQ

### Cursor EVAL bullets

1. Completions are `........` period collapses — not curated golds.  
2. Every gen trial keeps `wall_ms>0` and `n_new>0`.  
3. Do **not** PROMOTE open-chat / smarter LM from LOOKUP-only.

## Finding

1. Final dual-arm verify holds LOOKUP product quality (mean **9.0**, false-hit **0**).  
2. Generative arm remains period collapse (mean **1.0**) with honest `wall_ms>0` telemetry.  
3. Gate closes as **HOLD** (allowed by §5 AH6) — do **not** PROMOTE open-chat / smarter LM.  
4. **Ship claim unchanged:** scoped **AF packaged stack** — not open chat LM.

## Reproduce

```bash
npm run nano:ah:session
npm run nano:ah:hitl
npm run nano:test && npm run verify
```

## Artifacts

- Summary: `results/nano-lm/wave-ah/ah_hitl_summary.json`  
- Trials: `AH-FINAL-LOOKUP-HITL-01…10` · `AH-FINAL-GEN-HITL-01…10`  
- Contract: `nano_lm/tests/test_ah_hitl.py`

Next: **AH7 AH-REPORT**.
