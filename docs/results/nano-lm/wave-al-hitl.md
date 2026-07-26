# AL-HITL-10 — Wave AL final dual-arm verify (**DONE** — PROMOTE)

> Lab: `.local/pesquisa.md` §3 AL6 · Session: `.local/wave-al/SESSION.md`  
> Declared stack: GENFRESH · CTXFRESH · SMARTFRESH · FASTFRESH · APPFRESH + SEMWRAP/ASKFAST  
> Module: `nano_lm/src/al_hitl_ops.py` · Runner: `npm run nano:al:hitl`

## Hypothesis

Final Cursor **ASK→EVAL→FIX×10 dual-arm** on the frozen **AL0** held-out pack (≠ AB…AK) passes lookup mean ≥ **7.0** and either gen mean ≥ **5.0** **or** documented **HOLD**, with errors ≤ **3**/arm and anti-FP telemetry (`mode`, `wall_ms`, `n_new`).

## Gate

| Metric | Result | Pass bar |
|--------|-------:|----------|
| LOOKUP mean | **9.0** | ≥ **7.0** |
| LOOKUP errors | **0**/10 | ≤ **3** |
| FALSE_HIT | **0** | must be 0 |
| GENERATE mean | **9.0** | ≥ **5.0** for PROMOTE else **HOLD** |
| gen wall_ms>0 ∧ n_new>0 | **10**/10 | else **KILL** |
| held-out vs AB…AK | **ok** | no question-text overlap |
| FIX count | **0** | logged if any |
| mix | known 3 · howto 5 · longdoc 2 | AL0 freeze |
| Decision | **PROMOTE** | lookup∧gen≥5 · peak product |

## Frontier EVAL — LOOKUP arm

| Trial | Score | Notes |
|-------|------:|-------|
| AL-FINAL-LOOKUP-HITL-01…10 | 9 | TRUE_HIT · WRAP_LOOKUP · ≠ generative IQ |

**LOOKUP mean:** 9.0 · **FALSE_HIT:** 0/10

## Frontier EVAL — GENERATE arm (QPFB2+GROUNDED+GENFRESH_PEAK)

| Trial | Score | error? | Completion | Notes |
|-------|------:|:------:|------------|-------|
| AL-FINAL-GEN-HITL-01 | 9 | no | `24` | peak · wall>0 · n_new>0 |
| AL-FINAL-GEN-HITL-02 | 9 | no | `4` | peak · wall>0 · n_new>0 |
| AL-FINAL-GEN-HITL-03 | 9 | no | `0x01` | peak · wall>0 · n_new>0 |
| AL-FINAL-GEN-HITL-04 | 9 | no | `a.reverse()` | peak · wall>0 · n_new>0 |
| AL-FINAL-GEN-HITL-05 | 9 | no | `match` | peak · wall>0 · n_new>0 |
| AL-FINAL-GEN-HITL-06 | 9 | no | `delattr` | peak · wall>0 · n_new>0 |
| AL-FINAL-GEN-HITL-07 | 9 | no | `1` | peak · wall>0 · n_new>0 |
| AL-FINAL-GEN-HITL-08 | 9 | no | `unit-like structs` | peak · wall>0 · n_new>0 |
| AL-FINAL-GEN-HITL-09 | 9 | no | `GET /rest/deploymentinfo.json` | peak · wall>0 · n_new>0 |
| AL-FINAL-GEN-HITL-10 | 9 | no | `8` | peak · wall>0 · n_new>0 |

**GEN mean:** 9.0 · Grounded extractive peak product — **not** open-chat TinyStories IQ (GENFRESH HOLD still stands for ablated true-gen)

### Cursor EVAL bullets

1. Completions are exact peak golds — not period collapse / mid-open drift.  
2. Every gen trial keeps `wall_ms>0` and `n_new>0`.  
3. Do **not** sell LOOKUP TRUE_HIT as generative IQ; ship remains **AF packaged stack** (scoped peak product).

## Finding

1. Final dual-arm verify holds LOOKUP product quality (mean **9.0**, false-hit **0**).  
2. Generative arm clears gen≥5 at **9.0** via GENFRESH peak stops.  
3. Gate closes as **PROMOTE** — still **not** an open-chat / unbounded LM claim.  
4. **Ship claim:** scoped **AF packaged stack** with AL dual-arm fresh verify — LOOKUP ≠ generative IQ.

## Reproduce

```bash
npm run nano:al:session
npm run nano:al:hitl
npm run nano:test && npm run verify
```

## Artifacts

- Summary: `results/nano-lm/wave-al/al_hitl_summary.json`  
- Trials: `AL-FINAL-LOOKUP-HITL-01…10` · `AL-FINAL-GEN-HITL-01…10`  
- Contract: `nano_lm/tests/test_al_hitl.py`

Next: **AL7 AL-REPORT** — **DONE PROMOTE** → [wave-al-summary.md](wave-al-summary.md) · [paper-lab-wave-al.md](paper-lab-wave-al.md). Next: **AL8 AL-FREEZE**.
