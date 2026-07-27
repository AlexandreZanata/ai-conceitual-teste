# H-SMARTBASE — smarter cite + gen beyond SMARTCORE (**DONE** — PROMOTE)

> Lab: `.local/pesquisa.md` §3 AP3 · Session: `.local/wave-ap/SESSION.md`  
> Parent: **H-CTXBASE** · Pack: AP0 + trideca-hop paraphrases (CTXBASE companions)  
> Module: `nano_lm/src/smartbase_ops.py` · Runner: `npm run nano:smartbase` (`nano:ap:smartbase`)

## Hypothesis

Beat **GENBASE ablated** and peer **SMARTCORE** on dual-arm **cite + gen**: adversarial **trideca-hop** paraphrases still TRUE_HIT with cite≥8/10 and false-hit≈0, and GENERATE mean ≥ **5.0** under GENBASE grounded+extractive peak rubric **or** honest **HOLD** — never LOOKUP-as-IQ / peak-as-open-chat.

## Gate (Cursor ASK→EVAL→FIX×10 dual-arm)

| Metric | Result | Pass bar / rule |
|--------|-------:|-----------------|
| LOOKUP mean | **9.0** | ≥ **7.0** · WRAP_LOOKUP on paraphrase |
| GENERATE mean | **9.0** | ≥ **5.0** for PROMOTE else **HOLD** |
| cite_ok | **10**/10 | ≥ **8** |
| FALSE_HIT | **0**/10 | any → **KILL** |
| period collapses | **0**/10 | anti-period held (`..` exact gold FIX) |
| extractive peak used | **10**/10 | GENBASE AP-aware peak stops |
| beats GENBASE ablated 4.0 | **yes** (+5.0) | peak lifts factual gen |
| peer SMARTCORE gen 9.0 | **match** | trideca-hop advances cite stress |
| FIX count | **1** (`..` ≠ period collapse) | — |
| Decision | **PROMOTE** | lookup+cite+gen≥5 |

## Frontier EVAL — LOOKUP arm (trideca-hop paraphrase)

| Trial | Score | Notes |
|-------|------:|-------|
| AP-SMARTBASE-LOOKUP-HITL-01…10 | 9 | TRUE_HIT · cite_ok · wall_ms=0 · ≠ gen IQ |

**LOOKUP mean:** 9.0 · **FALSE_HIT:** 0/10 · CTXBASE distractors present; product retrieve only

## Frontier EVAL — GENERATE arm (QPFB2+BEAMKV+GROUNDED+ANTI_PERIOD+GENBASE_PEAK)

| Trial | Score | error? | Completion | Notes |
|-------|------:|:------:|------------|-------|
| AP-SMARTBASE-GEN-HITL-01 | 9 | no | `CS = ENT / 32` | peak |
| AP-SMARTBASE-GEN-HITL-02 | 9 | no | `0x00000000` | peak |
| AP-SMARTBASE-GEN-HITL-03 | 9 | no | `P2WPKH` | peak |
| AP-SMARTBASE-GEN-HITL-04 | 9 | no | `a.append(x)` | peak |
| AP-SMARTBASE-GEN-HITL-05 | 9 | no | `pass` | peak |
| AP-SMARTBASE-GEN-HITL-06 | 9 | no | `issubclass` | peak |
| AP-SMARTBASE-GEN-HITL-07 | 9 | no | `isize or usize` | peak |
| AP-SMARTBASE-GEN-HITL-08 | 9 | no | `..` | peak · FIX struct-update |
| AP-SMARTBASE-GEN-HITL-09 | 9 | no | `GET /rest/tx/<TX-HASH>.<bin\|hex\|json>` | peak |
| AP-SMARTBASE-GEN-HITL-10 | 9 | no | `8` | peak |

**GEN mean:** 9.0 · Periods **0**/10 · exact gold via GENBASE extractive peak (labeled ≠ open-chat IQ)

### Cursor EVAL bullets

1. Trideca-hop paraphrase LOOKUP holds cite to primary source despite twelve companion distractors.  
2. GENERATE reuses GENBASE peak (decode wall_ms>0 ∧ n_new>0) — exact short answers.  
3. Gen **9.0** beats GENBASE ablated **4.0** and peers SMARTCORE — scoped grounded peak product, **not** open-chat LM IQ (GENBASE HOLD still stands for ablated true-gen).

## Finding

1. Trideca-hop paraphrase LOOKUP holds (mean **9.0**, cite **10**/10, false-hit **0**).  
2. GENERATE via GENBASE peak mean **9.0** — peers SMARTCORE; beats GENBASE ablated **4.0**.  
3. Gen ≥ **5.0** under honest Cursor → **PROMOTE** per §3 AP3.  
4. Ship claim remains **AF packaged stack**; ≤5M stays.

## Reproduce

```bash
npm run nano:ap:session
npm run nano:smartbase
# alias: npm run nano:ap:smartbase
npm run nano:test && npm run verify
```

## Artifacts

- Summary: `results/nano-lm/wave-ap/smartbase_summary.json`  
- Trials: `AP-SMARTBASE-{LOOKUP|GEN}-HITL-01…10`  
- Contract: `nano_lm/tests/test_smartbase.py`

Next: **AP4 H-FASTBASE** — faster than FASTCORE at quality floor.
