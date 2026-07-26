# H-SMARTREAL — smarter retrieve + real gen EVAL (**DONE** — HOLD)

> Lab: `.local/pesquisa.md` §5 AG3 · Session: `.local/wave-ag/SESSION.md`  
> Parent: **H-SMARTULTRA** · **H-CTXREAL** · **H-ANTIFP** · Pack: AG0 held-out asks  
> Module: `nano_lm/src/smartreal_ops.py` · Runner: `npm run nano:smartreal` (`nano:ag:smartreal`)

## Hypothesis

Stress **SEMWRAP retrieve + primary cite** on **quad-hop adversarial paraphrases** of AG0, while running a real **GENERATE** arm via **QPFB2+BEAMKV** scored by Cursor on the completion — gen mean ≥ **5.0** **or** honest **HOLD**; false-hit ≈ 0 on lookup; never claim LOOKUP as generative IQ.

## Gate (Cursor ASK→EVAL→FIX×10 dual-arm)

| Metric | Result | Pass bar / rule |
|--------|-------:|-----------------|
| LOOKUP mean | **9.0** | ≥ **7.0** · labeled WRAP_LOOKUP |
| GENERATE mean | **4.0** | ≥ **5.0** for PROMOTE else **HOLD** |
| FALSE_HIT | **0**/10 | any → **KILL** |
| cite_ok (primary) | **10**/10 | ≥ **8**/10 |
| beats SERVEALIGN 3.4 | **yes** (+0.6) | smarter than AA2 open decode |
| FIX count | **0** | — |
| Decision | **HOLD** | lookup+cite ok; gen < 5 (honest) |

## Frontier EVAL — LOOKUP arm

| Trial | Score | cite? | Notes |
|-------|------:|:-----:|-------|
| AG-SMARTREAL-LOOKUP-HITL-01…10 | 9 | yes | TRUE_HIT · WRAP_LOOKUP · quad distractors ignored · ≠ gen IQ |

**LOOKUP mean:** 9.0 · **FALSE_HIT:** 0/10 · product retrieve/cite only

## Frontier EVAL — GENERATE arm (QPFB2+BEAMKV)

| Trial | Score | error? | Notes |
|-------|------:|:------:|-------|
| AG-SMARTREAL-GEN-HITL-01…10 | 4 | yes | non-period TinyStories-ish text · ≠ gold · wall_ms>0 · n_new=64 |

**GEN mean:** 4.0 · Beats SERVEALIGN **3.4** and raw periods **1.0** · still fails curated golds → **not** open chat IQ

## Finding

1. Quad-hop paraphrases recover correct golds with **0** FALSE_HIT and cite_ok **10**/10.  
2. QPFB2+BEAMKV generative arm produces real wall-timed completions (mean 4.0) — better than period collapse, below gen≥5.  
3. Gate closes as **HOLD** (allowed by §5 AG3) — do **not** PROMOTE smarter LM from LOOKUP alone.  
4. Ship claim remains **AF packaged stack**.

## Reproduce

```bash
npm run nano:ag:session
npm run nano:antifp
npm run nano:ctxreal
npm run nano:smartreal
# alias: npm run nano:ag:smartreal
npm run nano:test && npm run verify
```

## Artifacts

- Summary: `results/nano-lm/wave-ag/smartreal_summary.json`  
- Trials: `AG-SMARTREAL-LOOKUP-HITL-01…10` · `AG-SMARTREAL-GEN-HITL-01…10`  
- Contract: `nano_lm/tests/test_smartreal.py`

Next: **AG4 H-FASTREAL**.
