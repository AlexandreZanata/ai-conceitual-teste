# H-SMARTPEAK — smarter cite + gen beyond SMARTPUSH (**DONE** — PROMOTE)

> Lab: `.local/pesquisa.md` §3 AJ3 · Session: `.local/wave-aj/SESSION.md`  
> Parent: **H-CTXPEAK** · **H-GENPEAK** · Pack: AJ0 + hepta-hop paraphrases (CTXPEAK companions)  
> Module: `nano_lm/src/smartpeak_ops.py` · Runner: `npm run nano:smartpeak` (`nano:aj:smartpeak`)

## Hypothesis

Beat **SMARTPUSH** on dual-arm **cite + gen**: adversarial **hepta-hop** paraphrases still TRUE_HIT with cite≥8/10, and GENERATE mean ≥ **5.0** under GENPEAK grounded+extractive peak rubric **or** honest **HOLD** — never LOOKUP-as-IQ.

## Gate (Cursor ASK→EVAL→FIX×10 dual-arm)

| Metric | Result | Pass bar / rule |
|--------|-------:|-----------------|
| LOOKUP mean | **9.0** | ≥ **7.0** · WRAP_LOOKUP on paraphrase |
| GENERATE mean | **9.0** | ≥ **5.0** for PROMOTE else **HOLD** |
| cite_ok | **10**/10 | ≥ **8** |
| FALSE_HIT | **0**/10 | any → **KILL** |
| period collapses | **0**/10 | anti-period held |
| extractive peak used | **10**/10 | GENPEAK peak stops |
| beats SMARTPUSH gen 4.0 | **yes** (+5.0) | peak lifts factual gen |
| FIX count | **0** | — |
| Decision | **PROMOTE** | lookup+cite+gen≥5 |

## Frontier EVAL — LOOKUP arm (hepta-hop paraphrase)

| Trial | Score | Notes |
|-------|------:|-------|
| AJ-SMARTPEAK-LOOKUP-HITL-01…10 | 9 | TRUE_HIT · cite_ok · wall_ms=0 · ≠ gen IQ |

**LOOKUP mean:** 9.0 · **FALSE_HIT:** 0/10 · CTXPEAK distractors present; product retrieve only

## Frontier EVAL — GENERATE arm (QPFB2+BEAMKV+GROUNDED+ANTI_PERIOD+PEAK)

| Trial | Score | error? | Completion | Notes |
|-------|------:|:------:|------------|-------|
| AJ-SMARTPEAK-GEN-HITL-01 | 9 | no | `32` | peak · wall≈150 · n_new=64 |
| AJ-SMARTPEAK-GEN-HITL-02 | 9 | no | `1` | peak · wall≈98 · n_new=64 |
| AJ-SMARTPEAK-GEN-HITL-03 | 9 | no | `P2WSH` | peak · wall≈99 · n_new=64 |
| AJ-SMARTPEAK-GEN-HITL-04 | 9 | no | `collections.deque` | peak · wall≈97 · n_new=64 |
| AJ-SMARTPEAK-GEN-HITL-05 | 9 | no | `continue` | peak · wall≈103 · n_new=64 |
| AJ-SMARTPEAK-GEN-HITL-06 | 9 | no | `isinstance` | peak · wall≈99 · n_new=64 |
| AJ-SMARTPEAK-GEN-HITL-07 | 9 | no | `i32` | peak · wall≈100 · n_new=64 |
| AJ-SMARTPEAK-GEN-HITL-08 | 9 | no | `field init shorthand` | peak · wall≈98 · n_new=64 |
| AJ-SMARTPEAK-GEN-HITL-09 | 9 | no | `/wallet/<walletname>/` | peak · wall≈99 · n_new=64 |
| AJ-SMARTPEAK-GEN-HITL-10 | 9 | no | `Internet Header Length` | peak · wall≈99 · n_new=64 |

**GEN mean:** 9.0 · Periods **0**/10 · exact gold via extractive peak

### Cursor EVAL bullets

1. Hepta-hop paraphrase LOOKUP holds cite to primary source despite six companion distractors.  
2. GENERATE reuses GENPEAK peak (decode wall_ms>0 ∧ n_new=64) — exact short answers.  
3. Gen **9.0** beats SMARTPUSH **4.0** — scoped grounded peak product, **not** open-chat LM IQ.

## Finding

1. Hepta-hop paraphrase LOOKUP holds (mean **9.0**, cite **10**/10, false-hit **0**).  
2. GENERATE via GENPEAK peak mean **9.0** — beats SMARTPUSH gen **4.0**.  
3. Gen ≥ **5.0** under honest Cursor → **PROMOTE** per §3 AJ3.  
4. Ship claim remains **AF packaged stack**; ≤5M stays.

## Reproduce

```bash
npm run nano:aj:session
npm run nano:smartpeak
# alias: npm run nano:aj:smartpeak
npm run nano:test && npm run verify
```

## Artifacts

- Summary: `results/nano-lm/wave-aj/smartpeak_summary.json`  
- Trials: `AJ-SMARTPEAK-{LOOKUP|GEN}-HITL-01…10`  
- Contract: `nano_lm/tests/test_smartpeak.py`

Next: **AJ4 H-FASTPEAK**.
