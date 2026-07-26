# AG-HITL-10 — Wave AG final dual-arm verify (**DONE** — HOLD)

> Lab: `.local/pesquisa.md` §5 AG6 · Session: `.local/wave-ag/SESSION.md`  
> Declared stack: ANTIFP · CTXREAL · SMARTREAL · FASTREAL · APPREAL + SEMWRAP/ASKFAST  
> Module: `nano_lm/src/ag_hitl_ops.py` · Runner: `npm run nano:ag:hitl`

## Hypothesis

Final Cursor **ASK→EVAL→FIX×10 dual-arm** on the frozen **AG0** held-out pack (≠ AB…AF) passes lookup mean ≥ **7.0** and either gen mean ≥ **5.0** **or** documented **HOLD**, with errors ≤ **3**/arm and anti-FP telemetry (`mode`, `wall_ms`, `n_new`).

## Gate

| Metric | Result | Pass bar |
|--------|-------:|----------|
| LOOKUP mean | **9.0** | ≥ **7.0** |
| LOOKUP errors | **0**/10 | ≤ **3** |
| FALSE_HIT | **0** | must be 0 |
| GENERATE mean | **1.0** | ≥ **5.0** for PROMOTE else **HOLD** |
| gen wall_ms>0 ∧ n_new>0 | **10**/10 | else **KILL** |
| held-out vs AB…AF | **ok** | no question-text overlap |
| FIX count | **0** | logged if any |
| mix | known 3 · howto 5 · longdoc 2 | AG0 freeze |
| Decision | **HOLD** | lookup ok; gen &lt; 5 (documented) |

## Frontier EVAL — LOOKUP arm

| Trial | Score | Notes |
|-------|------:|-------|
| AG-FINAL-LOOKUP-HITL-01…10 | 9 | TRUE_HIT · WRAP_LOOKUP · ≠ generative IQ |

**LOOKUP mean:** 9.0 · **FALSE_HIT:** 0/10

## Frontier EVAL — GENERATE arm

| Trial | Score | error? | Notes |
|-------|------:|:------:|-------|
| AG-FINAL-GEN-HITL-01…10 | 1 | yes | QT+EARLY wrap=False · period collapse · wall_ms&gt;0 |

**GEN mean:** 1.0 · Peak smarter gen earlier in wave: SMARTREAL QPFB2 **4.0** (still &lt;5) · not open chat IQ

## Finding

1. Final dual-arm verify holds LOOKUP product quality (mean **9.0**, false-hit **0**).  
2. Generative arm remains period collapse (mean **1.0**) with honest `wall_ms>0` telemetry.  
3. Gate closes as **HOLD** (allowed by §5 AG6) — do **not** PROMOTE open-chat / smarter LM.  
4. **Ship claim unchanged:** scoped **AF packaged stack** — not open chat LM.

## Reproduce

```bash
npm run nano:ag:session
npm run nano:ag:hitl
npm run nano:test && npm run verify
```

## Artifacts

- Summary: `results/nano-lm/wave-ag/ag_hitl_summary.json`  
- Trials: `AG-FINAL-LOOKUP-HITL-01…10` · `AG-FINAL-GEN-HITL-01…10`  
- Contract: `nano_lm/tests/test_ag_hitl.py`

Next: **AG8 AG-FREEZE** (**DONE** — see [ag-freeze.md](ag-freeze.md)). Wave **AG COMPLETE + FROZEN**.
