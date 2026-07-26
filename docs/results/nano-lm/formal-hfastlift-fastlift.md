# H-FASTLIFT — faster generative ask vs AG FASTREAL (**DONE** — PROMOTE)

> Lab: `.local/pesquisa.md` §5 AH4 · Session: `.local/wave-ah/SESSION.md`  
> Parent: **H-FASTREAL** · Pack: AH0 held-out asks  
> Module: `nano_lm/src/fastlift_ops.py` · Runner: `npm run nano:fastlift` (`nano:ah:fastlift`)

## Hypothesis

Measure **real generative** wall/TTFT/e2e (wrap=False, `wall_ms>0`, `n_new>0`) with cold/warm/hot passes vs the **AG FASTREAL hot baseline** (~**16.1 ms**). LOOKUP arm remains product quality only — **never** claim LOOKUP `wall_ms=0` as speed IQ. Extra hot rounds (4) under max safe CPU threads.

## Gate (Cursor ASK→EVAL→FIX×10 dual-arm)

| Metric | Result | Pass bar / rule |
|--------|-------:|-----------------|
| LOOKUP mean | **9.0** | ≥ **7.0** · labeled WRAP_LOOKUP · ≠ speed IQ |
| GENERATE mean | **1.0** | logged honestly (period collapse) |
| FALSE_HIT | **0**/10 | any → **KILL** |
| gen wall_ms>0 ∧ n_new>0 | **10**/10 | else **KILL** |
| cold / warm / hot wall_ms | **26.0 / 12.0 / 11.6** | warm\|hot ↓ vs cold |
| vs FASTREAL hot (~16.1) | hot **11.6** | **beat** · numbers logged |
| e2e cold/warm/hot | **~3700 / 1274 / 1270** | ↓ vs cold · hot &lt; FASTREAL ~1371 |
| FIX count | **0** | — |
| Decision | **PROMOTE** | telemetry ∧ vs-FASTREAL ∧ lookup quality |

## Frontier EVAL — LOOKUP arm

| Trial | Score | Notes |
|-------|------:|-------|
| AH-FASTLIFT-LOOKUP-HITL-01…10 | 9 | TRUE_HIT · WRAP_LOOKUP · wall=0 · **not** speed IQ |

**LOOKUP mean:** 9.0 · **FALSE_HIT:** 0/10

## Frontier EVAL — GENERATE arm (QT+EARLY wrap=False)

| Trial | Score | error? | Notes |
|-------|------:|:------:|-------|
| AH-FASTLIFT-GEN-HITL-01…10 | 1 | yes | `........` period collapse · wall_ms>0 · n_new>0 · ≠ open chat IQ |

**GEN mean:** 1.0 · Speed claim only — quality still raw periods (same class as FASTREAL gen)

### Cursor EVAL bullets

1. Completions are period collapses — not curated golds.  
2. Telemetry holds: every gen trial has `wall_ms>0` and `n_new>0`.  
3. Hot wall **11.6 ms** beats FASTREAL hot **16.1 ms** (~**28%** drop) — PROMOTE is **speed**, not smarter LM.

## Finding

1. Generative warm/hot wall **~12 / 11.6 ms** beats cold **~26 ms** and sits below FASTREAL hot **16.1 ms**.  
2. All 10 gen trials keep `wall_ms>0` and `n_new>0` — anti-FP telemetry holds.  
3. LOOKUP stays mean **9.0** but is explicitly **not** used as speed IQ.  
4. Gen completions remain period collapse (mean **1.0**) — ship claim remains **AF packaged stack**.

## Reproduce

```bash
npm run nano:ah:session
npm run nano:fastlift
# alias: npm run nano:ah:fastlift
npm run nano:test && npm run verify
```

## Artifacts

- Summary: `results/nano-lm/wave-ah/fastlift_summary.json`  
- Trials: `AH-FASTLIFT-{LOOKUP|GEN}-HITL-01…10`  
- Contract: `nano_lm/tests/test_fastlift.py`

Next: **AH6 AH-HITL-10**.
