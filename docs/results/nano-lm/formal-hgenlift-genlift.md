# H-GENLIFT — lift generative completions (**DONE** — HOLD)

> Lab: `.local/pesquisa.md` §5 AH1 · Session: `.local/wave-ah/SESSION.md`  
> Parent: **H-ASKSMART** polish · **H-SMARTREAL** gen ceiling · Pack: AH0 held-out asks  
> Module: `nano_lm/src/genlift_ops.py` · Runner: `npm run nano:genlift` (`nano:ah:genlift`)

## Hypothesis

Lift **GENERATE** completions on AH0 via **QPFB2+BEAMKV + anti-period + stop framing** (ASKSMART knobs), dual-arm with LOOKUP product retrieve — gen mean ≥ **5.0** **or** honest **HOLD**; never claim LOOKUP as generative IQ.

## Gate (Cursor ASK→EVAL→FIX×10 dual-arm)

| Metric | Result | Pass bar / rule |
|--------|-------:|-----------------|
| LOOKUP mean | **9.0** | ≥ **7.0** · WRAP_LOOKUP |
| GENERATE mean | **4.0** | ≥ **5.0** for PROMOTE else **HOLD** |
| FALSE_HIT | **0**/10 | any → **KILL** |
| period collapses | **0**/10 | anti-period worked |
| beats SERVEALIGN 3.4 | **yes** (+0.6) | non-period open mid |
| beats SMARTREAL gen 4.0 | **no** (tie) | same open-completion ceiling |
| FIX count | **0** | — |
| Decision | **HOLD** | lookup ok; gen &lt; 5 (honest Cursor) |

## Frontier EVAL — LOOKUP arm

| Trial | Score | Notes |
|-------|------:|-------|
| AH-GENLIFT-LOOKUP-HITL-01…10 | 9 | TRUE_HIT · WRAP_LOOKUP · wall_ms=0 · ≠ gen IQ |

**LOOKUP mean:** 9.0 · **FALSE_HIT:** 0/10 · product retrieve only

## Frontier EVAL — GENERATE arm (QPFB2+BEAMKV+ANTI_PERIOD)

| Trial | Score | error? | Notes |
|-------|------:|:------:|-------|
| AH-GENLIFT-GEN-HITL-01…10 | 4 | yes | non-period TinyStories drift · ≠ gold · wall_ms≈97–160 · n_new=64 |

**GEN mean:** 4.0 · Periods **0**/10 (lift vs AG HITL gen **1.0** period collapse) · still fails curated golds → **not** open chat IQ

### Cursor EVAL bullets (per completion)

1. Anti-period + framed prompt removed `........` collapses.  
2. Completions are TinyStories-ish gibberish — not the curated fact.  
3. Open-completion rubric mid **4.0** (same SMARTREAL ceiling) — do **not** PROMOTE via ASKSMART floor-5 on any 4+ words.

## Finding

1. LOOKUP product path holds (mean **9.0**, false-hit **0**).  
2. ASKSMART polish lifts gen past period collapse (**0** periods; mean **4.0** vs AG HITL **1.0**).  
3. Gen still **&lt; 5.0** under honest Cursor / open rubric → **HOLD** per §5 AH1.  
4. Ship claim remains **AF packaged stack**.

## Reproduce

```bash
npm run nano:ah:session
npm run nano:genlift
# alias: npm run nano:ah:genlift
npm run nano:test && npm run verify
```

## Artifacts

- Summary: `results/nano-lm/wave-ah/genlift_summary.json`  
- Trials: `AH-GENLIFT-{LOOKUP|GEN}-HITL-01…10`  
- Contract: `nano_lm/tests/test_genlift.py`

Next: **AH2 H-CTXLIFT**.
