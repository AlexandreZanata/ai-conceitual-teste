# H-SMARTLIFT — smarter cite + gen beyond SMARTREAL (**DONE** — HOLD)

> Lab: `.local/pesquisa.md` §5 AH3 · Session: `.local/wave-ah/SESSION.md`  
> Parent: **H-SMARTREAL** · **H-GENLIFT** · Pack: AH0 + penta-hop paraphrases  
> Module: `nano_lm/src/smartlift_ops.py` · Runner: `npm run nano:smartlift` (`nano:ah:smartlift`)

## Hypothesis

Beat **SMARTREAL** on dual-arm **cite + gen**: adversarial **penta-hop** paraphrases still TRUE_HIT with cite≥8/10, and GENERATE mean ≥ **5.0** under honest open-completion rubric **or** honest **HOLD** — never LOOKUP-as-IQ / ASKSMART floor-5 on gibberish.

## Gate (Cursor ASK→EVAL→FIX×10 dual-arm)

| Metric | Result | Pass bar / rule |
|--------|-------:|-----------------|
| LOOKUP mean | **9.0** | ≥ **7.0** · WRAP_LOOKUP on paraphrase |
| GENERATE mean | **4.0** | ≥ **5.0** for PROMOTE else **HOLD** |
| cite_ok | **10**/10 | ≥ **8** |
| FALSE_HIT | **0**/10 | any → **KILL** |
| period collapses | **0**/10 | anti-period held |
| beats SMARTREAL gen 4.0 | **no** (tie) | same open mid ceiling |
| beats SERVEALIGN 3.4 | **yes** (+0.6) | non-period open mid |
| FIX count | **0** | — |
| Decision | **HOLD** | lookup+cite ok; gen &lt; 5 |

## Frontier EVAL — LOOKUP arm (penta-hop paraphrase)

| Trial | Score | Notes |
|-------|------:|-------|
| AH-SMARTLIFT-LOOKUP-HITL-01…10 | 9 | TRUE_HIT · cite_ok · wall_ms=0 · ≠ gen IQ |

**LOOKUP mean:** 9.0 · **FALSE_HIT:** 0/10 · distractors present; product retrieve only

## Frontier EVAL — GENERATE arm (QPFB2+BEAMKV+ANTI_PERIOD)

| Trial | Score | error? | Notes |
|-------|------:|:------:|-------|
| AH-SMARTLIFT-GEN-HITL-01…10 | 4 | yes | non-period TinyStories drift · ≠ gold · wall_ms≈99–153 · n_new=64 |

**GEN mean:** 4.0 · Periods **0**/10 · fails curated golds → **not** open chat IQ

### Cursor EVAL bullets (per completion)

1. Anti-period framing kept completions non-`........` (same GENLIFT lift).  
2. Text is TinyStories-ish word salad — not the AH0 gold fact.  
3. Open-completion mid **4.0** ties SMARTREAL — do **not** PROMOTE via ASKSMART floor-5.

## Finding

1. Penta-hop paraphrase LOOKUP holds (mean **9.0**, cite **10**/10, false-hit **0**).  
2. GENERATE path reuses GENLIFT decode; mean stays **4.0** — does **not** beat SMARTREAL gen.  
3. Gen **&lt; 5.0** under honest Cursor → **HOLD** per §5 AH3.  
4. Ship claim remains **AF packaged stack**.

## Reproduce

```bash
npm run nano:ah:session
npm run nano:smartlift
# alias: npm run nano:ah:smartlift
npm run nano:test && npm run verify
```

## Artifacts

- Summary: `results/nano-lm/wave-ah/smartlift_summary.json`  
- Trials: `AH-SMARTLIFT-{LOOKUP|GEN}-HITL-01…10`  
- Contract: `nano_lm/tests/test_smartlift.py`

Next: **AH5 H-APPLIFT**.
