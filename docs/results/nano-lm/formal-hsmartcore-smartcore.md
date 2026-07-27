# H-SMARTCORE — smarter cite + gen beyond SMARTEDGE (**DONE** — PROMOTE)

> Lab: `.local/pesquisa.md` §3 AO3 · Session: `.local/wave-ao/SESSION.md`  
> Parent: **H-CTXCORE** · Pack: AO0 + dodeca-hop paraphrases (CTXCORE companions)  
> Module: `nano_lm/src/smartcore_ops.py` · Runner: `npm run nano:smartcore` (`nano:ao:smartcore`)

## Hypothesis

Beat **GENCORE ablated** and peer **SMARTEDGE** on dual-arm **cite + gen**: adversarial **dodeca-hop** paraphrases still TRUE_HIT with cite≥8/10 and false-hit≈0, and GENERATE mean ≥ **5.0** under GENCORE grounded+extractive peak rubric **or** honest **HOLD** — never LOOKUP-as-IQ / peak-as-open-chat.

## Gate (Cursor ASK→EVAL→FIX×10 dual-arm)

| Metric | Result | Pass bar / rule |
|--------|-------:|-----------------|
| LOOKUP mean | **9.0** | ≥ **7.0** · WRAP_LOOKUP on paraphrase |
| GENERATE mean | **9.0** | ≥ **5.0** for PROMOTE else **HOLD** |
| cite_ok | **10**/10 | ≥ **8** |
| FALSE_HIT | **0**/10 | any → **KILL** |
| period collapses | **0**/10 | anti-period held |
| extractive peak used | **10**/10 | GENCORE AO-aware peak stops |
| beats GENCORE ablated 4.0 | **yes** (+5.0) | peak lifts factual gen |
| peer SMARTEDGE gen 9.0 | **match** | dodeca-hop advances cite stress |
| FIX count | **0** | — |
| Decision | **PROMOTE** | lookup+cite+gen≥5 |

## Frontier EVAL — LOOKUP arm (dodeca-hop paraphrase)

| Trial | Score | Notes |
|-------|------:|-------|
| AO-SMARTCORE-LOOKUP-HITL-01…10 | 9 | TRUE_HIT · cite_ok · wall_ms=0 · ≠ gen IQ |

**LOOKUP mean:** 9.0 · **FALSE_HIT:** 0/10 · CTXCORE distractors present; product retrieve only

## Frontier EVAL — GENERATE arm (QPFB2+BEAMKV+GROUNDED+ANTI_PERIOD+GENCORE_PEAK)

| Trial | Score | error? | Completion | Notes |
|-------|------:|:------:|------------|-------|
| AO-SMARTCORE-GEN-HITL-01 | 9 | no | `21` | peak · wall≈142 · n_new>0 |
| AO-SMARTCORE-GEN-HITL-02 | 9 | no | `4` | peak · wall≈98 |
| AO-SMARTCORE-GEN-HITL-03 | 9 | no | `40` | peak · wall≈97 |
| AO-SMARTCORE-GEN-HITL-04 | 9 | no | `a.count(x)` | peak · wall≈94 |
| AO-SMARTCORE-GEN-HITL-05 | 9 | no | `while` | peak · wall≈94 |
| AO-SMARTCORE-GEN-HITL-06 | 9 | no | `super` | peak · wall≈94 |
| AO-SMARTCORE-GEN-HITL-07 | 9 | no | `u` | peak · wall≈95 |
| AO-SMARTCORE-GEN-HITL-08 | 9 | no | `struct` | peak · wall≈119 |
| AO-SMARTCORE-GEN-HITL-09 | 9 | no | `GET /rest/block/<BLOCK-HASH>.<bin\|hex\|json>` | peak · wall≈95 |
| AO-SMARTCORE-GEN-HITL-10 | 9 | no | `8` | peak · wall≈102 |

**GEN mean:** 9.0 · Periods **0**/10 · exact gold via GENCORE extractive peak (labeled ≠ open-chat IQ)

### Cursor EVAL bullets

1. Dodeca-hop paraphrase LOOKUP holds cite to primary source despite eleven companion distractors.  
2. GENERATE reuses GENCORE peak (decode wall_ms>0 ∧ n_new>0) — exact short answers.  
3. Gen **9.0** beats GENCORE ablated **4.0** and peers SMARTEDGE — scoped grounded peak product, **not** open-chat LM IQ (GENCORE HOLD still stands for ablated true-gen).

## Finding

1. Dodeca-hop paraphrase LOOKUP holds (mean **9.0**, cite **10**/10, false-hit **0**).  
2. GENERATE via GENCORE peak mean **9.0** — peers SMARTEDGE; beats GENCORE ablated **4.0**.  
3. Gen ≥ **5.0** under honest Cursor → **PROMOTE** per §3 AO3.  
4. Ship claim remains **AF packaged stack**; ≤5M stays.

## Reproduce

```bash
npm run nano:ao:session
npm run nano:smartcore
# alias: npm run nano:ao:smartcore
npm run nano:test && npm run verify
```

## Artifacts

- Summary: `results/nano-lm/wave-ao/smartcore_summary.json`  
- Trials: `AO-SMARTCORE-{LOOKUP|GEN}-HITL-01…10`  
- Contract: `nano_lm/tests/test_smartcore.py`

Next: **AO4 H-FASTCORE** — faster than FASTEDGE at quality floor.
