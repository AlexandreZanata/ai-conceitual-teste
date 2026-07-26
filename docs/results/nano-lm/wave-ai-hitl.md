# AI-HITL-10 — Wave AI final dual-arm verify (**DONE** — HOLD)

> Lab: `.local/pesquisa.md` §5 AI6 · Session: `.local/wave-ai/SESSION.md`  
> Declared stack: GENPLUS · CTXPUSH · SMARTPUSH · FASTPUSH · APPPUSH + SEMWRAP/ASKFAST  
> Module: `nano_lm/src/ai_hitl_ops.py` · Runner: `npm run nano:ai:hitl`

## Hypothesis

Final Cursor **ASK→EVAL→FIX×10 dual-arm** on the frozen **AI0** held-out pack (≠ AB…AH) passes lookup mean ≥ **7.0** and either gen mean ≥ **5.0** **or** documented **HOLD**, with errors ≤ **3**/arm and anti-FP telemetry (`mode`, `wall_ms`, `n_new`).

## Gate

| Metric | Result | Pass bar |
|--------|-------:|----------|
| LOOKUP mean | **9.0** | ≥ **7.0** |
| LOOKUP errors | **0**/10 | ≤ **3** |
| FALSE_HIT | **0** | must be 0 |
| GENERATE mean | **4.0** | ≥ **5.0** for PROMOTE else **HOLD** |
| gen wall_ms>0 ∧ n_new>0 | **10**/10 | else **KILL** |
| held-out vs AB…AH | **ok** | no question-text overlap |
| FIX count | **0** | logged if any |
| mix | known 3 · howto 5 · longdoc 2 | AI0 freeze |
| Decision | **HOLD** | lookup ok; gen &lt; 5 (documented) |

## Frontier EVAL — LOOKUP arm

| Trial | Score | Notes |
|-------|------:|-------|
| AI-FINAL-LOOKUP-HITL-01…10 | 9 | TRUE_HIT · WRAP_LOOKUP · ≠ generative IQ |

**LOOKUP mean:** 9.0 · **FALSE_HIT:** 0/10

## Frontier EVAL — GENERATE arm

| Trial | Score | error? | Notes |
|-------|------:|:------:|-------|
| AI-FINAL-GEN-HITL-01…10 | 4 | yes | QPFB2+GROUNDED · TinyStories mid · wall_ms&gt;0 · n_new&gt;0 |

**GEN mean:** 4.0 · Matches wave peak (GENPLUS / SMARTPUSH / APPPUSH) · still &lt;5 · not open chat IQ

### Cursor EVAL bullets

1. Completions are non-period TinyStories drift — not curated golds.  
2. Every gen trial keeps `wall_ms>0` and `n_new>0`.  
3. Do **not** PROMOTE open-chat / smarter LM from LOOKUP-only.

## Finding

1. Final dual-arm verify holds LOOKUP product quality (mean **9.0**, false-hit **0**).  
2. Generative arm stays mid **4.0** (grounded path; beats AH final periods **1.0**) with honest telemetry.  
3. Gate closes as **HOLD** (allowed by §5 AI6) — do **not** PROMOTE open-chat / smarter LM.  
4. **Ship claim unchanged:** scoped **AF packaged stack** — not open chat LM.

## Reproduce

```bash
npm run nano:ai:session
npm run nano:ai:hitl
npm run nano:test && npm run verify
```

## Artifacts

- Summary: `results/nano-lm/wave-ai/ai_hitl_summary.json`  
- Trials: `AI-FINAL-LOOKUP-HITL-01…10` · `AI-FINAL-GEN-HITL-01…10`  
- Contract: `nano_lm/tests/test_ai_hitl.py`

Next: **AI7 AI-REPORT** (**DONE — PROMOTE** — [wave-ai-summary.md](wave-ai-summary.md) · [paper-lab-wave-ai.md](paper-lab-wave-ai.md)). **AI8 AI-FREEZE** (**DONE — PROMOTE** — [ai-freeze.md](ai-freeze.md) · [formal-haifreeze-ai-freeze.md](formal-haifreeze-ai-freeze.md)).
