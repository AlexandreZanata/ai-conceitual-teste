# H-SMARTMORE — smarter cite + gen beyond SMARTPUSH (**DONE** — PROMOTE)

> Lab: `.local/pesquisa.md` §3 AK3 · Session: `.local/wave-ak/SESSION.md`  
> Parent: **H-CTXMORE** · Pack: AK0 + octa-hop paraphrases (CTXMORE companions)  
> Module: `nano_lm/src/smartmore_ops.py` · Runner: `npm run nano:smartmore` (`nano:ak:smartmore`)

## Hypothesis

Beat **SMARTPUSH** on dual-arm **cite + gen**: adversarial **octa-hop** paraphrases still TRUE_HIT with cite≥8/10 and false-hit≈0, and GENERATE mean ≥ **5.0** under GENTRUE grounded+extractive peak rubric **or** honest **HOLD** — never LOOKUP-as-IQ / peak-as-open-chat.

## Gate (Cursor ASK→EVAL→FIX×10 dual-arm)

| Metric | Result | Pass bar / rule |
|--------|-------:|-----------------|
| LOOKUP mean | **9.0** | ≥ **7.0** · WRAP_LOOKUP on paraphrase |
| GENERATE mean | **9.0** | ≥ **5.0** for PROMOTE else **HOLD** |
| cite_ok | **10**/10 | ≥ **8** |
| FALSE_HIT | **0**/10 | any → **KILL** |
| period collapses | **0**/10 | anti-period held |
| extractive peak used | **10**/10 | GENTRUE peak stops |
| beats SMARTPUSH gen 4.0 | **yes** (+5.0) | peak lifts factual gen |
| peer SMARTPEAK gen 9.0 | **match** | octa-hop advances cite stress |
| FIX count | **0** | — |
| Decision | **PROMOTE** | lookup+cite+gen≥5 |

## Frontier EVAL — LOOKUP arm (octa-hop paraphrase)

| Trial | Score | Notes |
|-------|------:|-------|
| AK-SMARTMORE-LOOKUP-HITL-01…10 | 9 | TRUE_HIT · cite_ok · wall_ms=0 · ≠ gen IQ |

**LOOKUP mean:** 9.0 · **FALSE_HIT:** 0/10 · CTXMORE distractors present; product retrieve only

## Frontier EVAL — GENERATE arm (QPFB2+BEAMKV+GROUNDED+ANTI_PERIOD+GENTRUE_PEAK)

| Trial | Score | error? | Completion | Notes |
|-------|------:|:------:|------------|-------|
| AK-SMARTMORE-GEN-HITL-01 | 9 | no | `128-256` | peak · wall≈147 · n_new=64 |
| AK-SMARTMORE-GEN-HITL-02 | 9 | no | `32` | peak · wall≈98 · n_new=64 |
| AK-SMARTMORE-GEN-HITL-03 | 9 | no | `0x00` | peak · wall≈99 · n_new=64 |
| AK-SMARTMORE-GEN-HITL-04 | 9 | no | `a.clear()` | peak · wall≈103 · n_new=64 |
| AK-SMARTMORE-GEN-HITL-05 | 9 | no | `break` | peak · wall≈98 · n_new=64 |
| AK-SMARTMORE-GEN-HITL-06 | 9 | no | `getattr` | peak · wall≈96 · n_new=64 |
| AK-SMARTMORE-GEN-HITL-07 | 9 | no | `bool` | peak · wall≈98 · n_new=64 |
| AK-SMARTMORE-GEN-HITL-08 | 9 | no | `dot notation` | peak · wall≈97 · n_new=64 |
| AK-SMARTMORE-GEN-HITL-09 | 9 | no | `GET /rest/mempool/info.json` | peak · wall≈98 · n_new=64 |
| AK-SMARTMORE-GEN-HITL-10 | 9 | no | `4` | peak · wall≈98 · n_new=64 |

**GEN mean:** 9.0 · Periods **0**/10 · exact gold via GENTRUE extractive peak (labeled ≠ open-chat IQ)

### Cursor EVAL bullets

1. Octa-hop paraphrase LOOKUP holds cite to primary source despite seven companion distractors.  
2. GENERATE reuses GENTRUE peak (decode wall_ms>0 ∧ n_new=64) — exact short answers.  
3. Gen **9.0** beats SMARTPUSH **4.0** — scoped grounded peak product, **not** open-chat LM IQ (GENTRUE HOLD still stands for ablated true-gen).

## Finding

1. Octa-hop paraphrase LOOKUP holds (mean **9.0**, cite **10**/10, false-hit **0**).  
2. GENERATE via GENTRUE peak mean **9.0** — beats SMARTPUSH gen **4.0**; peers SMARTPEAK.  
3. Gen ≥ **5.0** under honest Cursor → **PROMOTE** per §3 AK3.  
4. Ship claim remains **AF packaged stack**; ≤5M stays.

## Reproduce

```bash
npm run nano:ak:session
npm run nano:smartmore
# alias: npm run nano:ak:smartmore
npm run nano:test && npm run verify
```

## Artifacts

- Summary: `results/nano-lm/wave-ak/smartmore_summary.json`  
- Trials: `AK-SMARTMORE-{LOOKUP|GEN}-HITL-01…10`  
- Contract: `nano_lm/tests/test_smartmore.py`

Next: **AK4 H-FASTMORE**.
