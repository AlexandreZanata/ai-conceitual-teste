# H-FASTPUSH — faster generative ask vs AH FASTLIFT (**DONE** — PROMOTE)

> Lab: `.local/pesquisa.md` §5 AI4 · Session: `.local/wave-ai/SESSION.md`  
> Parent: **H-FASTLIFT** · Pack: AI0 held-out asks  
> Module: `nano_lm/src/fastpush_ops.py` · Runner: `npm run nano:fastpush` (`nano:ai:fastpush`)

## Hypothesis

Measure **real generative** wall/TTFT/e2e (wrap=False, `wall_ms>0`, `n_new>0`) with cold/warm/hot passes vs the **AH FASTLIFT hot baseline** (~**11.6 ms**). LOOKUP arm remains product quality only — **never** claim LOOKUP `wall_ms=0` as speed IQ. Extra hot rounds (6) under max safe CPU threads.

## Gate (Cursor ASK→EVAL→FIX×10 dual-arm)

| Metric | Result | Pass bar / rule |
|--------|-------:|-----------------|
| LOOKUP mean | **9.0** | ≥ **7.0** · labeled WRAP_LOOKUP · ≠ speed IQ |
| GENERATE mean | **1.0** | logged honestly (period collapse) |
| FALSE_HIT | **0**/10 | any → **KILL** |
| gen wall_ms>0 ∧ n_new>0 | **10**/10 | else **KILL** |
| cold / warm / hot wall_ms | **24.5 / 10.6 / 10.7** | warm\|hot ↓ vs cold |
| vs FASTLIFT hot (~11.6) | hot **10.7** · warm **10.6** | **beat** · numbers logged |
| e2e cold/warm/hot | **~3644 / 1268 / 1209** | ↓ vs cold · hot &lt; FASTLIFT ~1270 |
| FIX count | **0** | — |
| Decision | **PROMOTE** | telemetry ∧ vs-FASTLIFT ∧ lookup quality |

## Frontier EVAL — LOOKUP arm

| Trial | Score | Notes |
|-------|------:|-------|
| AI-FASTPUSH-LOOKUP-HITL-01…10 | 9 | TRUE_HIT · WRAP_LOOKUP · wall=0 · **not** speed IQ |

**LOOKUP mean:** 9.0 · **FALSE_HIT:** 0/10

## Frontier EVAL — GENERATE arm (QT+EARLY wrap=False)

| Trial | Score | error? | Notes |
|-------|------:|:------:|-------|
| AI-FASTPUSH-GEN-HITL-01…10 | 1 | yes | `........` period collapse · wall_ms>0 · n_new>0 · ≠ open chat IQ |

**GEN mean:** 1.0 · Speed claim only — quality still raw periods (same class as FASTLIFT gen)

### Cursor EVAL bullets

1. Completions are period collapses — not curated golds.  
2. Telemetry holds: every gen trial has `wall_ms>0` and `n_new>0`.  
3. Hot wall **10.7 ms** / warm **10.6 ms** beat FASTLIFT hot **11.6 ms** — PROMOTE is **speed**, not smarter LM.

## Finding

1. Generative warm/hot wall **~10.6 / 10.7 ms** beats cold **~24.5 ms** and sits below FASTLIFT hot **11.6 ms**.  
2. Hot e2e **~1209 ms** beats FASTLIFT hot e2e **~1270 ms**.  
3. All 10 gen trials keep `wall_ms>0` and `n_new>0` — anti-FP telemetry holds.  
4. LOOKUP stays mean **9.0** but is explicitly **not** used as speed IQ.  
5. Gen completions remain period collapse (mean **1.0**) — ship claim remains **AF packaged stack**.

## Reproduce

```bash
npm run nano:ai:session
npm run nano:fastpush
# alias: npm run nano:ai:fastpush
npm run nano:test && npm run verify
```

## Artifacts

- Summary: `results/nano-lm/wave-ai/fastpush_summary.json`  
- Trials: `AI-FASTPUSH-{LOOKUP|GEN}-HITL-01…10`  
- Contract: `nano_lm/tests/test_fastpush.py`

Next: **AI5 H-APPPUSH** (**DONE — HOLD** — [formal-happpush-apppush.md](formal-happpush-apppush.md)). Next: **AI6 AI-HITL-10**.
