# H-SMARTEDGE — smarter cite + gen beyond SMARTNEXT (**DONE** — PROMOTE)

> Lab: `.local/pesquisa.md` §3 AN3 · Session: `.local/wave-an/SESSION.md`  
> Parent: **H-CTXEDGE** · Pack: AN0 + undeca-hop paraphrases (CTXEDGE companions)  
> Module: `nano_lm/src/smartedge_ops.py` · Runner: `npm run nano:smartedge` (`nano:an:smartedge`)

## Hypothesis

Beat **GENEDGE ablated** and peer **SMARTNEXT** on dual-arm **cite + gen**: adversarial **undeca-hop** paraphrases still TRUE_HIT with cite≥8/10 and false-hit≈0, and GENERATE mean ≥ **5.0** under GENEDGE grounded+extractive peak rubric **or** honest **HOLD** — never LOOKUP-as-IQ / peak-as-open-chat.

## Gate (Cursor ASK→EVAL→FIX×10 dual-arm)

| Metric | Result | Pass bar / rule |
|--------|-------:|-----------------|
| LOOKUP mean | **9.0** | ≥ **7.0** · WRAP_LOOKUP on paraphrase |
| GENERATE mean | **9.0** | ≥ **5.0** for PROMOTE else **HOLD** |
| cite_ok | **10**/10 | ≥ **8** |
| FALSE_HIT | **0**/10 | any → **KILL** |
| period collapses | **0**/10 | anti-period held |
| extractive peak used | **10**/10 | GENEDGE AN-aware peak stops |
| beats GENEDGE ablated 4.0 | **yes** (+5.0) | peak lifts factual gen |
| peer SMARTNEXT gen 9.0 | **match** | undeca-hop advances cite stress |
| FIX count | **0** | — |
| Decision | **PROMOTE** | lookup+cite+gen≥5 |

## Frontier EVAL — LOOKUP arm (undeca-hop paraphrase)

| Trial | Score | Notes |
|-------|------:|-------|
| AN-SMARTEDGE-LOOKUP-HITL-01…10 | 9 | TRUE_HIT · cite_ok · wall_ms=0 · ≠ gen IQ |

**LOOKUP mean:** 9.0 · **FALSE_HIT:** 0/10 · CTXEDGE distractors present; product retrieve only

## Frontier EVAL — GENERATE arm (QPFB2+BEAMKV+GROUNDED+ANTI_PERIOD+GENEDGE_PEAK)

| Trial | Score | error? | Completion | Notes |
|-------|------:|:------:|------------|-------|
| AN-SMARTEDGE-GEN-HITL-01 | 9 | no | `18` | peak · wall≈196 · n_new>0 |
| AN-SMARTEDGE-GEN-HITL-02 | 9 | no | `4` | peak · wall≈122 |
| AN-SMARTEDGE-GEN-HITL-03 | 9 | no | `10000` | peak · wall≈116 |
| AN-SMARTEDGE-GEN-HITL-04 | 9 | no | `a.remove(x)` | peak · wall≈116 |
| AN-SMARTEDGE-GEN-HITL-05 | 9 | no | `range` | peak · wall≈112 |
| AN-SMARTEDGE-GEN-HITL-06 | 9 | no | `__dict__` | peak · wall≈122 |
| AN-SMARTEDGE-GEN-HITL-07 | 9 | no | `tuples and arrays` | peak · wall≈111 |
| AN-SMARTEDGE-GEN-HITL-08 | 9 | no | `tuple structs` | peak · wall≈131 |
| AN-SMARTEDGE-GEN-HITL-09 | 9 | no | `GET /rest/headers/<BLOCK-HASH>.<bin\|hex\|json>` | peak · wall≈149 |
| AN-SMARTEDGE-GEN-HITL-10 | 9 | no | `16` | peak · wall≈146 |

**GEN mean:** 9.0 · Periods **0**/10 · exact gold via GENEDGE extractive peak (labeled ≠ open-chat IQ)

### Cursor EVAL bullets

1. Undeca-hop paraphrase LOOKUP holds cite to primary source despite ten companion distractors.  
2. GENERATE reuses GENEDGE peak (decode wall_ms>0 ∧ n_new>0) — exact short answers.  
3. Gen **9.0** beats GENEDGE ablated **4.0** and peers SMARTNEXT — scoped grounded peak product, **not** open-chat LM IQ (GENEDGE HOLD still stands for ablated true-gen).

## Finding

1. Undeca-hop paraphrase LOOKUP holds (mean **9.0**, cite **10**/10, false-hit **0**).  
2. GENERATE via GENEDGE peak mean **9.0** — peers SMARTNEXT; beats GENEDGE ablated **4.0**.  
3. Gen ≥ **5.0** under honest Cursor → **PROMOTE** per §3 AN3.  
4. Ship claim remains **AF packaged stack**; ≤5M stays.

## Reproduce

```bash
npm run nano:an:session
npm run nano:smartedge
# alias: npm run nano:an:smartedge
npm run nano:test && npm run verify
```

## Artifacts

- Summary: `results/nano-lm/wave-an/smartedge_summary.json`  
- Trials: `AN-SMARTEDGE-{LOOKUP|GEN}-HITL-01…10`  
- Contract: `nano_lm/tests/test_smartedge.py`

Next: **AN4 H-FASTEDGE** — faster than FASTNEXT at quality floor.
