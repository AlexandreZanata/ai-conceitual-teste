# H-GENPLUS — push generative completions (**DONE** — HOLD)

> Lab: `.local/pesquisa.md` §5 AI1 · Session: `.local/wave-ai/SESSION.md`  
> Parent: **AI0 SESSION** PROMOTE · Pack: AI0 held-out asks  
> Module: `nano_lm/src/genplus_ops.py` · Runner: `npm run nano:genplus` (`nano:ai:genplus` / `nano:genpush`)

## Hypothesis

Push **GENERATE** past AH **H-GENLIFT** (gen mean 4.0) via **QPFB2+BEAMKV + curated grounding + anti-period + context-prefer beam pick**, dual-arm with LOOKUP product retrieve — gen mean ≥ **5.0** **or** honest **HOLD**; never claim LOOKUP as generative IQ.

## Gate (Cursor ASK→EVAL→FIX×10 dual-arm)

| Metric | Result | Pass bar / rule |
|--------|-------:|-----------------|
| LOOKUP mean | **9.0** | ≥ **7.0** · WRAP_LOOKUP |
| GENERATE mean | **4.0** | ≥ **5.0** for PROMOTE else **HOLD** |
| FALSE_HIT | **0**/10 | any → **KILL** |
| period collapses | **0**/10 | anti-period held |
| beats GENLIFT gen 4.0 | **no** (tie) | same open-completion ceiling |
| FIX attempts | **10**/10 | batch re-ground; **0** score lifts |
| Decision | **HOLD** | lookup ok; gen &lt; 5 (honest Cursor) |

## Frontier EVAL — LOOKUP arm

| Trial | Score | Notes |
|-------|------:|-------|
| AI-GENPLUS-LOOKUP-HITL-01…10 | 9 | TRUE_HIT · WRAP_LOOKUP · wall_ms=0 · ≠ gen IQ |

**LOOKUP mean:** 9.0 · **FALSE_HIT:** 0/10 · product retrieve only

## Frontier EVAL — GENERATE arm (QPFB2+BEAMKV+GROUNDED+ANTI_PERIOD)

| Trial | Score | error? | Notes |
|-------|------:|:------:|-------|
| AI-GENPLUS-GEN-HITL-01…10 | 4 | yes | TinyStories drift · ≠ gold · wall_ms≈100–152 · n_new=64 |

**GEN mean:** 4.0 · Periods **0**/10 · grounded context did **not** copy curated facts → **not** open chat IQ

### Cursor EVAL bullets (per completion)

1. Grounded top-k chunks + short-answer frame; prompts capped under student `max_position=512`.  
2. Completions remain TinyStories-ish gibberish — gold never contained.  
3. Open/grounded rubric mid **4.0** (tie GENLIFT) — do **not** PROMOTE via LOOKUP arm.

## Finding

1. LOOKUP product path holds (mean **9.0**, false-hit **0**).  
2. Grounding + context-prefer pick removes period risk but does **not** lift factual gen.  
3. Gen still **&lt; 5.0** under honest Cursor → **HOLD** per §5 AI1.  
4. Ship claim remains **AF packaged stack**.  
5. Optional next: **AI1b H-CAPRENEG** — **DONE HOLD** (keep ≤5M); then **AI2 H-CTXPUSH**.

## Reproduce

```bash
npm run nano:ai:session
npm run nano:genplus
# aliases: npm run nano:ai:genplus · npm run nano:genpush
npm run nano:test && npm run verify
```

## Artifacts

- Summary: `results/nano-lm/wave-ai/genplus_summary.json`  
- Trials: `AI-GENPLUS-{LOOKUP|GEN}-HITL-01…10`  
- Contract: `nano_lm/tests/test_genplus.py`

Next: **AI1b H-CAPRENEG** (**DONE — HOLD** — [formal-hcapreneg-capreneg.md](formal-hcapreneg-capreneg.md)). Next: **AI2 H-CTXPUSH**.
