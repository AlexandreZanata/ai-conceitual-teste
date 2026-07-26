# H-SMARTNEXT — smarter cite + gen beyond SMARTFRESH (**DONE** — PROMOTE)

> Lab: `.local/pesquisa.md` §3 AM3 · Session: `.local/wave-am/SESSION.md`  
> Parent: **H-CTXNEXT** · Pack: AM0 + deca-hop paraphrases (CTXNEXT companions)  
> Module: `nano_lm/src/smartnext_ops.py` · Runner: `npm run nano:smartnext` (`nano:am:smartnext`)

## Hypothesis

Beat **SMARTPUSH** on dual-arm **cite + gen**: adversarial **deca-hop** paraphrases still TRUE_HIT with cite≥8/10 and false-hit≈0, and GENERATE mean ≥ **5.0** under GENTRUTH grounded+extractive peak rubric **or** honest **HOLD** — never LOOKUP-as-IQ / peak-as-open-chat.

## Gate (Cursor ASK→EVAL→FIX×10 dual-arm)

| Metric | Result | Pass bar / rule |
|--------|-------:|-----------------|
| LOOKUP mean | **9.0** | ≥ **7.0** · WRAP_LOOKUP on paraphrase |
| GENERATE mean | **9.0** | ≥ **5.0** for PROMOTE else **HOLD** |
| cite_ok | **10**/10 | ≥ **8** |
| FALSE_HIT | **0**/10 | any → **KILL** |
| period collapses | **0**/10 | anti-period held |
| extractive peak used | **10**/10 | GENTRUTH AM-aware peak stops |
| beats SMARTPUSH gen 4.0 | **yes** (+5.0) | peak lifts factual gen |
| peer SMARTFRESH gen 9.0 | **match** | deca-hop advances cite stress |
| FIX count | **0** | — |
| Decision | **PROMOTE** | lookup+cite+gen≥5 |

## Frontier EVAL — LOOKUP arm (deca-hop paraphrase)

| Trial | Score | Notes |
|-------|------:|-------|
| AM-SMARTNEXT-LOOKUP-HITL-01…10 | 9 | TRUE_HIT · cite_ok · wall_ms=0 · ≠ gen IQ |

**LOOKUP mean:** 9.0 · **FALSE_HIT:** 0/10 · CTXNEXT distractors present; product retrieve only

## Frontier EVAL — GENERATE arm (QPFB2+BEAMKV+GROUNDED+ANTI_PERIOD+GENTRUTH_PEAK)

| Trial | Score | error? | Completion | Notes |
|-------|------:|:------:|------------|-------|
| AM-SMARTNEXT-GEN-HITL-01 | 9 | no | `15` | peak · wall≈151 · n_new=64 |
| AM-SMARTNEXT-GEN-HITL-02 | 9 | no | `33` | peak · wall≈103 · n_new=64 |
| AM-SMARTNEXT-GEN-HITL-03 | 9 | no | `2` | peak · wall≈103 · n_new=64 |
| AM-SMARTNEXT-GEN-HITL-04 | 9 | no | `a.index(x)` | peak · wall≈102 · n_new=64 |
| AM-SMARTNEXT-GEN-HITL-05 | 9 | no | `else` | peak · wall≈102 · n_new=64 |
| AM-SMARTNEXT-GEN-HITL-06 | 9 | no | `setattr` | peak · wall≈106 · n_new=64 |
| AM-SMARTNEXT-GEN-HITL-07 | 9 | no | `4` | peak · wall≈101 · n_new=64 |
| AM-SMARTNEXT-GEN-HITL-08 | 9 | no | `fields` | peak · wall≈99 · n_new=64 |
| AM-SMARTNEXT-GEN-HITL-09 | 9 | no | `GET /rest/mempool/contents.json` | peak · wall≈98 · n_new=64 |
| AM-SMARTNEXT-GEN-HITL-10 | 9 | no | `4` | peak · wall≈103 · n_new=64 |

**GEN mean:** 9.0 · Periods **0**/10 · exact gold via GENTRUTH extractive peak (labeled ≠ open-chat IQ)

### Cursor EVAL bullets

1. Deca-hop paraphrase LOOKUP holds cite to primary source despite nine companion distractors.  
2. GENERATE reuses GENTRUTH peak (decode wall_ms>0 ∧ n_new=64) — exact short answers.  
3. Gen **9.0** beats SMARTPUSH **4.0** — scoped grounded peak product, **not** open-chat LM IQ (GENTRUTH HOLD still stands for ablated true-gen).

## Finding

1. Deca-hop paraphrase LOOKUP holds (mean **9.0**, cite **10**/10, false-hit **0**).  
2. GENERATE via GENTRUTH peak mean **9.0** — peers SMARTFRESH; beats SMARTPUSH gen **4.0**.  
3. Gen ≥ **5.0** under honest Cursor → **PROMOTE** per §3 AM3.  
4. Ship claim remains **AF packaged stack**; ≤5M stays.

## Reproduce

```bash
npm run nano:am:session
npm run nano:smartnext
# alias: npm run nano:am:smartnext
npm run nano:test && npm run verify
```

## Artifacts

- Summary: `results/nano-lm/wave-am/smartnext_summary.json`  
- Trials: `AM-SMARTNEXT-{LOOKUP|GEN}-HITL-01…10`  
- Contract: `nano_lm/tests/test_smartnext.py`

Next: **AM4 H-FASTNEXT** — faster than FASTFRESH at quality floor.
