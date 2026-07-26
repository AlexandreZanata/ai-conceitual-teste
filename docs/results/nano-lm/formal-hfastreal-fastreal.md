# H-FASTREAL — faster generative ask vs AF raw (**DONE** — PROMOTE)

> Lab: `.local/pesquisa.md` §5 AG4 · Session: `.local/wave-ag/SESSION.md`  
> Parent: **H-FASTULTRA** · **H-ANTIFP** · Pack: AG0 held-out asks  
> Module: `nano_lm/src/fastreal_ops.py` · Runner: `npm run nano:fastreal` (`nano:ag:fastreal`)

## Hypothesis

Measure **real generative** wall/TTFT/e2e (wrap=False, `wall_ms>0`, `n_new>0`) with cold/warm/hot passes vs the **AF raw open-decode baseline** (`AB_OPEN_MEAN_WALL_MS` ≈ **25.179 ms**). LOOKUP arm remains product quality only — **never** claim FASTULTRA LOOKUP `wall_ms=0` as speed IQ.

## Gate (Cursor ASK→EVAL→FIX×10 dual-arm)

| Metric | Result | Pass bar / rule |
|--------|-------:|-----------------|
| LOOKUP mean | **9.0** | ≥ **7.0** · labeled WRAP_LOOKUP · ≠ speed IQ |
| GENERATE mean | **1.0** | logged honestly (period collapse) |
| FALSE_HIT | **0**/10 | any → **KILL** |
| gen wall_ms>0 ∧ n_new>0 | **10**/10 | else **KILL** |
| cold / warm / hot wall_ms | **35.2 / 16.3 / 16.1** | warm\|hot ↓ vs cold |
| vs AF raw open (~25.2) | warm/hot **~16.1** | numbers logged · hot &lt; AF raw |
| e2e cold/warm/hot | **~3942 / 1442 / 1371** | ↓ vs cold |
| FIX count | **0** | — |
| Decision | **PROMOTE** | telemetry ∧ speed ∧ lookup quality |

## Frontier EVAL — LOOKUP arm

| Trial | Score | Notes |
|-------|------:|-------|
| AG-FASTREAL-LOOKUP-HITL-01…10 | 9 | TRUE_HIT · WRAP_LOOKUP · wall=0 · **not** speed IQ |

**LOOKUP mean:** 9.0 · **FALSE_HIT:** 0/10

## Frontier EVAL — GENERATE arm (QT+EARLY wrap=False)

| Trial | Score | error? | Notes |
|-------|------:|:------:|-------|
| AG-FASTREAL-GEN-HITL-01…10 | 1 | yes | period collapse · wall_ms≈16–35 · n_new&gt;0 · ≠ open chat IQ |

**GEN mean:** 1.0 · Speed claim only — quality still raw periods (same as ANTIFP gen smoke)

## Finding

1. Generative warm/hot wall **~16 ms** beats cold **~35 ms** (~**54%** drop) and sits below AF raw open **~25.2 ms**.  
2. All 10 gen trials keep `wall_ms>0` and `n_new>0` — anti-FP telemetry holds.  
3. LOOKUP stays mean **9.0** but is explicitly **not** used as speed IQ.  
4. Gen completions remain period collapse (mean **1.0**) — PROMOTE is **speed**, not smarter LM. Ship claim remains **AF packaged stack**.

## Reproduce

```bash
npm run nano:ag:session
npm run nano:antifp
npm run nano:fastreal
# alias: npm run nano:ag:fastreal
npm run nano:test && npm run verify
```

## Artifacts

- Summary: `results/nano-lm/wave-ag/fastreal_summary.json`  
- Trials: `AG-FASTREAL-LOOKUP-HITL-01…10` · `AG-FASTREAL-GEN-HITL-01…10`  
- Contract: `nano_lm/tests/test_fastreal.py`

Next: **AG5 H-APPREAL**.
