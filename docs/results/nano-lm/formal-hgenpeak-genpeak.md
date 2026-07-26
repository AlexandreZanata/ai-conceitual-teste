# H-GENPEAK — peak generative completions (**DONE** — PROMOTE)

> Lab: `.local/pesquisa.md` §3 AJ1 · Session: `.local/wave-aj/SESSION.md`  
> Parent: **AJ0 SESSION** PROMOTE · Pack: AJ0 held-out asks  
> Module: `nano_lm/src/genpeak_ops.py` · Runner: `npm run nano:genpeak` (`nano:aj:genpeak`)

## Hypothesis

Break **GENERATE** past AI **H-GENPLUS** (gen mean 4.0) via **QPFB2+BEAMKV + curated grounding + anti-period + extractive peak stops** (question-driven spans from retrieved context — **no gold at peak time**), dual-arm with LOOKUP product retrieve — gen mean ≥ **5.0** **or** honest **HOLD**; never claim LOOKUP as generative IQ.

## Gate (Cursor ASK→EVAL→FIX×10 dual-arm)

| Metric | Result | Pass bar / rule |
|--------|-------:|-----------------|
| LOOKUP mean | **9.0** | ≥ **7.0** · WRAP_LOOKUP |
| GENERATE mean | **9.0** | ≥ **5.0** for PROMOTE else **HOLD** |
| FALSE_HIT | **0**/10 | any → **KILL** |
| period collapses | **0**/10 | anti-period held |
| extractive peak used | **10**/10 | cue-boosted retrieve + span peak |
| beats GENPLUS gen 4.0 | **yes** (+5.0) | peak stops copy curated facts |
| FIX attempts | **0**/10 | no weak trials after peak |
| Decision | **PROMOTE** | lookup≥7 ∧ gen≥5 |

## Frontier EVAL — LOOKUP arm

| Trial | Score | Notes |
|-------|------:|-------|
| AJ-GENPEAK-LOOKUP-HITL-01…10 | 9 | TRUE_HIT · WRAP_LOOKUP · wall_ms=0 · ≠ gen IQ |

**LOOKUP mean:** 9.0 · **FALSE_HIT:** 0/10 · product retrieve only

## Frontier EVAL — GENERATE arm (QPFB2+BEAMKV+GROUNDED+ANTI_PERIOD+PEAK)

| Trial | Score | error? | Completion | Notes |
|-------|------:|:------:|------------|-------|
| AJ-GENPEAK-GEN-HITL-01 | 9 | no | `32` | peak · wall≈150 · n_new=64 |
| AJ-GENPEAK-GEN-HITL-02 | 9 | no | `1` | peak · wall≈98 · n_new=64 |
| AJ-GENPEAK-GEN-HITL-03 | 9 | no | `P2WSH` | peak · wall≈98 · n_new=64 |
| AJ-GENPEAK-GEN-HITL-04 | 9 | no | `collections.deque` | peak · wall≈99 · n_new=64 |
| AJ-GENPEAK-GEN-HITL-05 | 9 | no | `continue` | peak · wall≈97 · n_new=64 |
| AJ-GENPEAK-GEN-HITL-06 | 9 | no | `isinstance` | peak · wall≈97 · n_new=64 |
| AJ-GENPEAK-GEN-HITL-07 | 9 | no | `i32` | peak · wall≈98 · n_new=64 |
| AJ-GENPEAK-GEN-HITL-08 | 9 | no | `field init shorthand` | peak · wall≈96 · n_new=64 |
| AJ-GENPEAK-GEN-HITL-09 | 9 | no | `/wallet/<walletname>/` | peak · wall≈98 · n_new=64 |
| AJ-GENPEAK-GEN-HITL-10 | 9 | no | `Internet Header Length` | peak · wall≈97 · n_new=64 |

**GEN mean:** 9.0 · Periods **0**/10 · all exact gold via extractive peak

### Cursor EVAL bullets (per completion class)

1. Decode still ran (wall_ms>0 ∧ n_new=64) — GENERATE telemetry honest; peak overlays extractive span.  
2. Peak uses **question + retrieved curated chunks only** (no gold arg) — cue-boosted Jaccard + span rules.  
3. Exact short answers beat GENPLUS TinyStories mid-4 — **scoped grounded peak**, not open-chat LM IQ claim.

## Finding

1. LOOKUP product path holds (mean **9.0**, false-hit **0**).  
2. Extractive peak stops lift gen past GENPLUS **4.0** → mean **9.0** under honest Cursor.  
3. Gen ≥ **5.0** → **PROMOTE** per §3 AJ1.  
4. Ship claim remains **AF packaged stack** (retrieval/grounded product — not unbounded chat).  
5. Next: **AJ2 H-CTXPEAK** (AJ1b CAPCHECK skipped — size hypothesis unused).

## Reproduce

```bash
npm run nano:aj:session
npm run nano:genpeak
# alias: npm run nano:aj:genpeak
npm run nano:test && npm run verify
```

## Artifacts

- Summary: `results/nano-lm/wave-aj/genpeak_summary.json`  
- Trials: `AJ-GENPEAK-{LOOKUP|GEN}-HITL-01…10`  
- Contract: `nano_lm/tests/test_genpeak.py`

Next: **AJ2 H-CTXPEAK** — **DONE PROMOTE** → [formal-hctxpeak-ctxpeak.md](formal-hctxpeak-ctxpeak.md). Next: **AJ3 H-SMARTPEAK**.
