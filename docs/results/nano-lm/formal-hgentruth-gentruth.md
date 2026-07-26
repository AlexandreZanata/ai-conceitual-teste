# H-GENTRUTH — true gen via peak ablation (**DONE** — HOLD)

> Lab: `.local/pesquisa.md` §3 AM1 · Session: `.local/wave-am/SESSION.md`  
> Parent: **AM0 SESSION** PROMOTE · Pack: AM0 held-out asks  
> Module: `nano_lm/src/gentruth_ops.py` · Runner: `npm run nano:gentruth` (`nano:am:gentruth`)

## Hypothesis

Chase **smarter GENERATE** on AM0 with **peak ablation** + **stricter gen label**: gate on **ablated** (`peak_off`) completions only; log extractive `peak_on` as comparison — never PROMOTE LOOKUP or peak tautology as open-chat IQ. Gen mean ≥ **5.0** **or** honest **HOLD**.

## Gate (Cursor ASK→EVAL→FIX×10 dual-arm)

| Metric | Result | Pass bar / rule |
|--------|-------:|-----------------|
| LOOKUP mean | **9.0** | ≥ **7.0** · WRAP_LOOKUP |
| GENERATE mean (**ablated**) | **4.0** | ≥ **5.0** for PROMOTE else **HOLD** |
| GENERATE peak_on mean | **9.0** | anti-FP compare only — **not** smarter-LM gate |
| peak_only_lift | **true** | peak≥5 ∧ ablated&lt;5 → must **HOLD** |
| FALSE_HIT | **0**/10 | any → **KILL** |
| period collapses | **0**/10 | anti-period held |
| extractive peak used (compare) | **10**/10 | AM-aware spans; labeled extractive |
| FIX attempts | **10**/10 ablated re-ground (0 lifts) · **1** peak extractor FIX (`char`→4) | re-ASK after FIX |
| Decision | **HOLD** | lookup ok; ablated gen &lt; 5 (honest) |

## Frontier EVAL — LOOKUP arm

| Trial | Score | Notes |
|-------|------:|-------|
| AM-GENTRUTH-LOOKUP-HITL-01…10 | 9 | TRUE_HIT · WRAP_LOOKUP · wall_ms=0 · ≠ gen IQ |

**LOOKUP mean:** 9.0 · **FALSE_HIT:** 0/10 · product retrieve only

## Frontier EVAL — GENERATE arm (ablated = gate)

| Trial | Ablated | Peak | error? | Notes |
|-------|--------:|-----:|:------:|-------|
| AM-GENTRUTH-GEN-HITL-01 | 4 | 9 | yes | TinyStories drift · peak `15` |
| AM-GENTRUTH-GEN-HITL-02 | 4 | 9 | yes | drift · peak `33` |
| AM-GENTRUTH-GEN-HITL-03 | 4 | 9 | yes | drift · peak `2` |
| AM-GENTRUTH-GEN-HITL-04 | 4 | 9 | yes | drift · peak `a.index(x)` |
| AM-GENTRUTH-GEN-HITL-05 | 4 | 9 | yes | drift · peak `else` |
| AM-GENTRUTH-GEN-HITL-06 | 4 | 9 | yes | drift · peak `setattr` |
| AM-GENTRUTH-GEN-HITL-07 | 4 | 9 | yes | drift · peak `4` (after FIX vs `U+10FFFF`) |
| AM-GENTRUTH-GEN-HITL-08 | 4 | 9 | yes | drift · peak `fields` |
| AM-GENTRUTH-GEN-HITL-09 | 4 | 9 | yes | drift · peak mempool contents path |
| AM-GENTRUTH-GEN-HITL-10 | 4 | 9 | yes | drift · peak `4` (IHL) |

**Ablated GEN mean:** 4.0 · **Peak compare mean:** 9.0 · Periods **0**/10 · wall_ms≈98–181 · n_new=64

### Cursor EVAL bullets

1. Ablated decode keeps GENERATE telemetry (`wall_ms>0`, `n_new=64`) but does not contain gold — mid **4.0** (tie GENFRESH / GENTRUE).  
2. Peak overlay copies curated spans exactly — **extractive assist**, not open-chat LM IQ.  
3. `peak_only_lift=true` forbids smarter-LM **PROMOTE** — HOLD per anti-FP doctrine.

## Finding

1. LOOKUP product path holds (mean **9.0**, false-hit **0**).  
2. Peak ablation proves AL/AK-style peak lift is **extractive**, not generative IQ.  
3. Ablated gen **&lt; 5.0** under honest Cursor → **HOLD** per §3 AM1.  
4. Ship claim remains **AF packaged stack** (+ optional peak path, labeled).  
5. Optional **AM1b H-CAPCHECK** skipped (size hypothesis unused) → next **AM2 H-CTXNEXT**.

## Reproduce

```bash
npm run nano:am:session
npm run nano:gentruth
# alias: npm run nano:am:gentruth
npm run nano:test && npm run verify
```

## Artifacts

- Summary: `results/nano-lm/wave-am/gentruth_summary.json`  
- Trials: `AM-GENTRUTH-{LOOKUP|GEN}-HITL-01…10`  
- Contract: `nano_lm/tests/test_gentruth.py`

Next: **AM2 H-CTXNEXT** — longer usable ctx beyond CTXFRESH.
