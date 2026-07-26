# H-SMARTFRESH — smarter cite + gen beyond SMARTMORE (**DONE** — PROMOTE)

> Lab: `.local/pesquisa.md` §3 AL3 · Session: `.local/wave-al/SESSION.md`  
> Parent: **H-CTXFRESH** · Pack: AL0 + nona-hop paraphrases (CTXFRESH companions)  
> Module: `nano_lm/src/smartfresh_ops.py` · Runner: `npm run nano:smartfresh` (`nano:al:smartfresh`)

## Hypothesis

Beat **SMARTPUSH** on dual-arm **cite + gen**: adversarial **nona-hop** paraphrases still TRUE_HIT with cite≥8/10 and false-hit≈0, and GENERATE mean ≥ **5.0** under GENFRESH grounded+extractive peak rubric **or** honest **HOLD** — never LOOKUP-as-IQ / peak-as-open-chat.

## Gate (Cursor ASK→EVAL→FIX×10 dual-arm)

| Metric | Result | Pass bar / rule |
|--------|-------:|-----------------|
| LOOKUP mean | **9.0** | ≥ **7.0** · WRAP_LOOKUP on paraphrase |
| GENERATE mean | **9.0** | ≥ **5.0** for PROMOTE else **HOLD** |
| cite_ok | **10**/10 | ≥ **8** |
| FALSE_HIT | **0**/10 | any → **KILL** |
| period collapses | **0**/10 | anti-period held |
| extractive peak used | **10**/10 | GENFRESH AL-aware peak stops |
| beats SMARTPUSH gen 4.0 | **yes** (+5.0) | peak lifts factual gen |
| peer SMARTMORE gen 9.0 | **match** | nona-hop advances cite stress |
| FIX count | **0** | — |
| Decision | **PROMOTE** | lookup+cite+gen≥5 |

## Frontier EVAL — LOOKUP arm (nona-hop paraphrase)

| Trial | Score | Notes |
|-------|------:|-------|
| AL-SMARTFRESH-LOOKUP-HITL-01…10 | 9 | TRUE_HIT · cite_ok · wall_ms=0 · ≠ gen IQ |

**LOOKUP mean:** 9.0 · **FALSE_HIT:** 0/10 · CTXFRESH distractors present; product retrieve only

## Frontier EVAL — GENERATE arm (QPFB2+BEAMKV+GROUNDED+ANTI_PERIOD+GENFRESH_PEAK)

| Trial | Score | error? | Completion | Notes |
|-------|------:|:------:|------------|-------|
| AL-SMARTFRESH-GEN-HITL-01 | 9 | no | `24` | peak · wall≈155 · n_new=64 |
| AL-SMARTFRESH-GEN-HITL-02 | 9 | no | `4` | peak · wall≈105 · n_new=64 |
| AL-SMARTFRESH-GEN-HITL-03 | 9 | no | `0x01` | peak · wall≈100 · n_new=64 |
| AL-SMARTFRESH-GEN-HITL-04 | 9 | no | `a.reverse()` | peak · wall≈102 · n_new=64 |
| AL-SMARTFRESH-GEN-HITL-05 | 9 | no | `match` | peak · wall≈103 · n_new=64 |
| AL-SMARTFRESH-GEN-HITL-06 | 9 | no | `delattr` | peak · wall≈102 · n_new=64 |
| AL-SMARTFRESH-GEN-HITL-07 | 9 | no | `1` | peak · wall≈100 · n_new=64 |
| AL-SMARTFRESH-GEN-HITL-08 | 9 | no | `unit-like structs` | peak · wall≈102 · n_new=64 |
| AL-SMARTFRESH-GEN-HITL-09 | 9 | no | `GET /rest/deploymentinfo.json` | peak · wall≈102 · n_new=64 |
| AL-SMARTFRESH-GEN-HITL-10 | 9 | no | `8` | peak · wall≈102 · n_new=64 |

**GEN mean:** 9.0 · Periods **0**/10 · exact gold via GENFRESH extractive peak (labeled ≠ open-chat IQ)

### Cursor EVAL bullets

1. Nona-hop paraphrase LOOKUP holds cite to primary source despite eight companion distractors.  
2. GENERATE reuses GENFRESH peak (decode wall_ms>0 ∧ n_new=64) — exact short answers.  
3. Gen **9.0** beats SMARTPUSH **4.0** — scoped grounded peak product, **not** open-chat LM IQ (GENFRESH HOLD still stands for ablated true-gen).

## Finding

1. Nona-hop paraphrase LOOKUP holds (mean **9.0**, cite **10**/10, false-hit **0**).  
2. GENERATE via GENFRESH peak mean **9.0** — peers SMARTMORE; beats SMARTPUSH gen **4.0**.  
3. Gen ≥ **5.0** under honest Cursor → **PROMOTE** per §3 AL3.  
4. Ship claim remains **AF packaged stack**; ≤5M stays.

## Reproduce

```bash
npm run nano:al:session
npm run nano:smartfresh
# alias: npm run nano:al:smartfresh
npm run nano:test && npm run verify
```

## Artifacts

- Summary: `results/nano-lm/wave-al/smartfresh_summary.json`  
- Trials: `AL-SMARTFRESH-{LOOKUP|GEN}-HITL-01…10`  
- Contract: `nano_lm/tests/test_smartfresh.py`

Next: **AL4 H-FASTFRESH** — **DONE PROMOTE** → [formal-hfastfresh-fastfresh.md](formal-hfastfresh-fastfresh.md).
