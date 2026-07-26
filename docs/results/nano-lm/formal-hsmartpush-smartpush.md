# H-SMARTPUSH — smarter cite + gen beyond SMARTLIFT (**DONE** — HOLD)

> Lab: `.local/pesquisa.md` §5 AI3 · Session: `.local/wave-ai/SESSION.md`  
> Parent: **H-SMARTLIFT** · **H-GENPLUS** · Pack: AI0 + hexa-hop paraphrases (CTXPUSH companions)  
> Module: `nano_lm/src/smartpush_ops.py` · Runner: `npm run nano:smartpush` (`nano:ai:smartpush`)

## Hypothesis

Beat **SMARTLIFT** on dual-arm **cite + gen**: adversarial **hexa-hop** paraphrases still TRUE_HIT with cite≥8/10, and GENERATE mean ≥ **5.0** under grounded QPFB2 rubric **or** honest **HOLD** — never LOOKUP-as-IQ.

## Gate (Cursor ASK→EVAL→FIX×10 dual-arm)

| Metric | Result | Pass bar / rule |
|--------|-------:|-----------------|
| LOOKUP mean | **9.0** | ≥ **7.0** · WRAP_LOOKUP on paraphrase |
| GENERATE mean | **4.0** | ≥ **5.0** for PROMOTE else **HOLD** |
| cite_ok | **10**/10 | ≥ **8** |
| FALSE_HIT | **0**/10 | any → **KILL** |
| period collapses | **0**/10 | anti-period held |
| beats SMARTLIFT gen 4.0 | **no** (tie) | same mid ceiling |
| beats SERVEALIGN 3.4 | **yes** (+0.6) | non-period open mid |
| FIX count | **0** | — |
| Decision | **HOLD** | lookup+cite ok; gen &lt; 5 |

## Frontier EVAL — LOOKUP arm (hexa-hop paraphrase)

| Trial | Score | Notes |
|-------|------:|-------|
| AI-SMARTPUSH-LOOKUP-HITL-01…10 | 9 | TRUE_HIT · cite_ok · wall_ms=0 · ≠ gen IQ |

**LOOKUP mean:** 9.0 · **FALSE_HIT:** 0/10 · CTXPUSH distractors present; product retrieve only

## Frontier EVAL — GENERATE arm (QPFB2+BEAMKV+GROUNDED+ANTI_PERIOD)

| Trial | Score | error? | Notes |
|-------|------:|:------:|-------|
| AI-SMARTPUSH-GEN-HITL-01…10 | 4 | yes | non-period TinyStories drift · ≠ gold · wall_ms>0 · n_new>0 |

**GEN mean:** 4.0 · Periods **0**/10 · fails curated golds → **not** open chat IQ

### Cursor EVAL bullets (per completion)

1. Grounded retrieve + anti-period kept completions non-`........` (same GENPLUS path).  
2. Text still TinyStories-ish / weak gold overlap — not the AI0 gold fact.  
3. Open/grounded mid **4.0** ties SMARTLIFT — do **not** PROMOTE via LOOKUP 9.0 alone.

## Finding

1. Hexa-hop paraphrase LOOKUP holds (mean **9.0**, cite **10**/10, false-hit **0**).  
2. GENERATE reuses GENPLUS grounded decode; mean stays **4.0** — does **not** beat SMARTLIFT gen.  
3. Gen **&lt; 5.0** under honest Cursor → **HOLD** per §5 AI3.  
4. Ship claim remains **AF packaged stack**; ≤5M stays.

## Reproduce

```bash
npm run nano:ai:session
npm run nano:smartpush
# alias: npm run nano:ai:smartpush
npm run nano:test && npm run verify
```

## Artifacts

- Summary: `results/nano-lm/wave-ai/smartpush_summary.json`  
- Trials: `AI-SMARTPUSH-{LOOKUP|GEN}-HITL-01…10`  
- Contract: `nano_lm/tests/test_smartpush.py`

Next: **AI4 H-FASTPUSH** (**DONE — PROMOTE** — [formal-hfastpush-fastpush.md](formal-hfastpush-fastpush.md)). Next: **AI5 H-APPPUSH**.
