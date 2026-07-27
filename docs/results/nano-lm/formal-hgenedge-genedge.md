# H-GENEDGE — true gen via peak ablation (**DONE** — HOLD)

> Lab: `.local/pesquisa.md` §3 AN1 · Session: `.local/wave-an/SESSION.md`  
> Parent: **AN0 SESSION** PROMOTE · Pack: AN0 held-out asks  
> Module: `nano_lm/src/genedge_ops.py` · Runner: `npm run nano:genedge` (`nano:an:genedge`)

## Hypothesis

Chase **smarter GENERATE** on AN0 with **peak ablation** + **stricter gen label**: gate on **ablated** (`peak_off`) completions only; log extractive `peak_on` as comparison — never PROMOTE LOOKUP or peak tautology as open-chat IQ. Gen mean ≥ **5.0** **or** honest **HOLD**.

## Gate (Cursor ASK→EVAL→FIX×10 dual-arm)

| Metric | Result | Pass bar / rule |
|--------|-------:|-----------------|
| LOOKUP mean | **9.0** | ≥ **7.0** · WRAP_LOOKUP |
| GENERATE mean (**ablated**) | **4.0** | ≥ **5.0** for PROMOTE else **HOLD** |
| GENERATE peak_on mean | **9.0** | anti-FP compare only — **not** smarter-LM gate |
| peak_only_lift | **true** | peak≥5 ∧ ablated&lt;5 → must **HOLD** |
| FALSE_HIT | **0**/10 | any → **KILL** |
| period collapses | **0**/10 | anti-period held |
| extractive peak used (compare) | **10**/10 | AN-aware spans; labeled extractive |
| FIX attempts | **0** | peak extractors hit gold on first pass |
| Decision | **HOLD** | lookup ok; ablated gen &lt; 5 (honest) |

## Frontier EVAL — LOOKUP arm

| Trial | Score | Notes |
|-------|------:|-------|
| AN-GENEDGE-LOOKUP-HITL-01…10 | 9 | TRUE_HIT · WRAP_LOOKUP · wall_ms=0 · ≠ gen IQ |

**LOOKUP mean:** 9.0 · **FALSE_HIT:** 0/10 · product retrieve only

## Frontier EVAL — GENERATE arm (ablated = gate)

| Trial | Ablated | Peak | error? | Notes |
|-------|--------:|-----:|:------:|-------|
| AN-GENEDGE-GEN-HITL-01 | 4 | 9 | yes | TinyStories drift · peak `18` |
| AN-GENEDGE-GEN-HITL-02 | 4 | 9 | yes | drift · peak `4` |
| AN-GENEDGE-GEN-HITL-03 | 4 | 9 | yes | drift · peak `10000` |
| AN-GENEDGE-GEN-HITL-04 | 4 | 9 | yes | drift · peak `a.remove(x)` |
| AN-GENEDGE-GEN-HITL-05 | 4 | 9 | yes | drift · peak `range` |
| AN-GENEDGE-GEN-HITL-06 | 4 | 9 | yes | drift · peak `__dict__` |
| AN-GENEDGE-GEN-HITL-07 | 4 | 9 | yes | drift · peak `tuples and arrays` |
| AN-GENEDGE-GEN-HITL-08 | 4 | 9 | yes | drift · peak `tuple structs` |
| AN-GENEDGE-GEN-HITL-09 | 4 | 9 | yes | drift · peak headers path |
| AN-GENEDGE-GEN-HITL-10 | 4 | 9 | yes | drift · peak `16` (Total Length) |

**Ablated GEN mean:** 4.0 · **Peak compare mean:** 9.0 · Periods **0**/10 · wall_ms≈103–407 · n_new&gt;0

### Cursor EVAL bullets

1. Ablated decode keeps GENERATE telemetry (`wall_ms>0`, `n_new>0`) but does not contain gold — mid **4.0** (ties GENTRUTH / GENFRESH / GENTRUE).  
2. Peak overlay copies curated spans exactly — **extractive assist**, not open-chat LM IQ.  
3. `peak_only_lift=true` forbids smarter-LM **PROMOTE** — HOLD per anti-FP doctrine.

## Finding

1. LOOKUP product path holds (mean **9.0**, false-hit **0**).  
2. Peak ablation proves AM-style peak lift is **extractive**, not generative IQ.  
3. Ablated gen **&lt; 5.0** under honest Cursor → **HOLD** per §3 AN1.  
4. Ship claim remains **AF packaged stack** (+ optional peak path, labeled).  
5. Optional **AN1b H-CAPCHECK** skipped (size hypothesis unused) → next **AN2 H-CTXEDGE** — **DONE PROMOTE**.

## Reproduce

```bash
npm run nano:an:session
npm run nano:genedge
# alias: npm run nano:an:genedge
npm run nano:test && npm run verify
```

## Artifacts

- Summary: `results/nano-lm/wave-an/genedge_summary.json`  
- Trials: `AN-GENEDGE-{LOOKUP|GEN}-HITL-01…10`  
- Contract: `nano_lm/tests/test_genedge.py`

Next: **AN2 H-CTXEDGE** — **DONE PROMOTE** → [formal-hctxedge-ctxedge.md](formal-hctxedge-ctxedge.md). Next **AN3 H-SMARTEDGE**.
