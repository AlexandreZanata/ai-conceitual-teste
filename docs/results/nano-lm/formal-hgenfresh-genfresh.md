# H-GENFRESH — true gen via peak ablation (**DONE** — HOLD)

> Lab: `.local/pesquisa.md` §3 AL1 · Session: `.local/wave-al/SESSION.md`  
> Parent: **AL0 SESSION** PROMOTE · Pack: AL0 held-out asks  
> Module: `nano_lm/src/genfresh_ops.py` · Runner: `npm run nano:genfresh` (`nano:al:genfresh`)

## Hypothesis

Chase **smarter GENERATE** on AL0 with **peak ablation** + **stricter gen label**: gate on **ablated** (`peak_off`) completions only; log extractive `peak_on` as comparison — never PROMOTE LOOKUP or peak tautology as open-chat IQ. Gen mean ≥ **5.0** **or** honest **HOLD**.

## Gate (Cursor ASK→EVAL→FIX×10 dual-arm)

| Metric | Result | Pass bar / rule |
|--------|-------:|-----------------|
| LOOKUP mean | **9.0** | ≥ **7.0** · WRAP_LOOKUP |
| GENERATE mean (**ablated**) | **4.0** | ≥ **5.0** for PROMOTE else **HOLD** |
| GENERATE peak_on mean | **9.0** | anti-FP compare only — **not** smarter-LM gate |
| peak_only_lift | **true** | peak≥5 ∧ ablated&lt;5 → must **HOLD** |
| FALSE_HIT | **0**/10 | any → **KILL** |
| period collapses | **0**/10 | anti-period held |
| extractive peak used (compare) | **10**/10 | AL-aware spans; labeled extractive |
| FIX attempts | **10**/10 | re-ground ablated; **0** score lifts |
| Decision | **HOLD** | lookup ok; ablated gen &lt; 5 (honest) |

## Frontier EVAL — LOOKUP arm

| Trial | Score | Notes |
|-------|------:|-------|
| AL-GENFRESH-LOOKUP-HITL-01…10 | 9 | TRUE_HIT · WRAP_LOOKUP · wall_ms=0 · ≠ gen IQ |

**LOOKUP mean:** 9.0 · **FALSE_HIT:** 0/10 · product retrieve only

## Frontier EVAL — GENERATE arm (ablated = gate)

| Trial | Ablated | Peak | error? | Notes |
|-------|--------:|-----:|:------:|-------|
| AL-GENFRESH-GEN-HITL-01 | 4 | 9 | yes | TinyStories drift · peak `24` |
| AL-GENFRESH-GEN-HITL-02 | 4 | 9 | yes | drift · peak `4` |
| AL-GENFRESH-GEN-HITL-03 | 4 | 9 | yes | drift · peak `0x01` |
| AL-GENFRESH-GEN-HITL-04 | 4 | 9 | yes | drift · peak `a.reverse()` |
| AL-GENFRESH-GEN-HITL-05 | 4 | 9 | yes | drift · peak `match` |
| AL-GENFRESH-GEN-HITL-06 | 4 | 9 | yes | drift · peak `delattr` |
| AL-GENFRESH-GEN-HITL-07 | 4 | 9 | yes | drift · peak `1` |
| AL-GENFRESH-GEN-HITL-08 | 4 | 9 | yes | drift · peak `unit-like structs` |
| AL-GENFRESH-GEN-HITL-09 | 4 | 9 | yes | drift · peak deploymentinfo path |
| AL-GENFRESH-GEN-HITL-10 | 4 | 9 | yes | drift · peak `8` |

**Ablated GEN mean:** 4.0 · **Peak compare mean:** 9.0 · Periods **0**/10 · wall_ms>0 · n_new>0

### Cursor EVAL bullets

1. Ablated decode keeps GENERATE telemetry (`wall_ms>0`, `n_new>0`) but does not contain gold — mid **4.0** (tie GENPLUS / GENTRUE).  
2. Peak overlay copies curated spans exactly — **extractive assist**, not open-chat LM IQ.  
3. `peak_only_lift=true` forbids smarter-LM **PROMOTE** — HOLD per anti-FP doctrine.

## Finding

1. LOOKUP product path holds (mean **9.0**, false-hit **0**).  
2. Peak ablation proves AK/AJ-style peak lift is **extractive**, not generative IQ.  
3. Ablated gen **&lt; 5.0** under honest Cursor → **HOLD** per §3 AL1.  
4. Ship claim remains **AF packaged stack** (+ optional peak path, labeled).  
5. Optional **AL1b H-CAPCHECK** skipped (size hypothesis unused) → next **AL2 H-CTXFRESH**.

## Reproduce

```bash
npm run nano:al:session
npm run nano:genfresh
# alias: npm run nano:al:genfresh
npm run nano:test && npm run verify
```

## Artifacts

- Summary: `results/nano-lm/wave-al/genfresh_summary.json`  
- Trials: `AL-GENFRESH-{LOOKUP|GEN}-HITL-01…10`  
- Contract: `nano_lm/tests/test_genfresh.py`

Next: **AL2 H-CTXFRESH** — longer usable ctx beyond CTXMORE.
