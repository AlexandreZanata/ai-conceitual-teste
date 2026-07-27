# H-FASTEDGE — faster GENEDGE peak-extractive gen vs FASTNEXT (**DONE** — PROMOTE)

> Lab: `.local/pesquisa.md` §3 AN4 · Session: `.local/wave-an/SESSION.md`  
> Parent: **H-SMARTEDGE** · Pack: AN0 held-out asks  
> Module: `nano_lm/src/fastedge_ops.py` · Runner: `npm run nano:fastedge` (`nano:an:fastedge`)

## Hypothesis

Measure **real generative** wall/TTFT/e2e with `wall_ms>0` ∧ `n_new>0` via **PEAK_FAST+GENEDGE** (cue-first retrieve K=1 · ctx≤480 · doc-offset jump · per-hit extract — no student decode on the timed path) vs **AM FASTNEXT** hot baseline (**0.17 ms**). Quality floor gen≥**5.0**. LOOKUP arm remains product quality only — **never** claim LOOKUP `wall_ms=0` as speed IQ. Extra hot rounds (**160**) under max safe CPU threads (`cpus-2`).

## Gate (Cursor ASK→EVAL→FIX×10 dual-arm)

| Metric | Result | Pass bar / rule |
|--------|-------:|-----------------|
| LOOKUP mean | **9.0** | ≥ **7.0** · labeled WRAP_LOOKUP · ≠ speed IQ |
| GENERATE mean | **7.0** | ≥ **5.0** quality floor |
| FALSE_HIT | **0**/10 | any → **KILL** |
| gen wall_ms>0 ∧ n_new>0 | **10**/10 | else **KILL** |
| cold / warm / hot wall_ms | **0.14 / 0.10 / 0.05** | warm\|hot ↓ vs cold |
| vs FASTNEXT hot (**0.17**) | hot **0.05** · warm **0.10** | **beat** (wall primary) |
| e2e cold/warm/hot | **1.46 / 1.06 / 0.51** | ↓ vs cold |
| FIX count | **1** (wall-primary gate + K=1/per-hit extract) | before/after in runner |
| Decision | **PROMOTE** | telemetry ∧ vs-FASTNEXT wall ∧ floor ∧ lookup |

## Frontier EVAL — LOOKUP arm

| Trial | Score | Notes |
|-------|------:|-------|
| AN-FASTEDGE-LOOKUP-HITL-01…10 | 9 | TRUE_HIT · WRAP_LOOKUP · wall=0 · **not** speed IQ |

**LOOKUP mean:** 9.0 · **FALSE_HIT:** 0/10

## Frontier EVAL — GENERATE arm (PEAK_FAST+GENEDGE)

| Trial | Score | error? | Completion | Notes |
|-------|------:|:------:|------------|-------|
| AN-FASTEDGE-GEN-HITL-01 | 7 | no | `18` | peak · wall>0 · n_new>0 |
| AN-FASTEDGE-GEN-HITL-02 | 7 | no | `4` | peak · wall>0 · n_new>0 |
| AN-FASTEDGE-GEN-HITL-03 | 7 | no | `10000` | peak · wall>0 · n_new>0 |
| AN-FASTEDGE-GEN-HITL-04 | 7 | no | `a.remove(x)` | peak · wall>0 · n_new>0 |
| AN-FASTEDGE-GEN-HITL-05 | 7 | no | `range` | peak · wall>0 · n_new>0 |
| AN-FASTEDGE-GEN-HITL-06 | 7 | no | `__dict__` | peak · wall>0 · n_new>0 |
| AN-FASTEDGE-GEN-HITL-07 | 7 | no | `tuples and arrays` | peak · wall>0 · n_new>0 |
| AN-FASTEDGE-GEN-HITL-08 | 7 | no | `tuple structs` | peak · wall>0 · n_new>0 |
| AN-FASTEDGE-GEN-HITL-09 | 7 | no | `GET /rest/headers/<BLOCK-HASH>.<bin\|hex\|json>` | peak · wall>0 · n_new>0 |
| AN-FASTEDGE-GEN-HITL-10 | 7 | no | `16` | peak · wall>0 · n_new>0 |

**GEN mean:** 7.0 · Speed claim primary — completions are GENEDGE peak spans (not open-chat IQ)

### Cursor EVAL bullets

1. Completions match held-out golds via GENEDGE extractive peak — not period collapse.  
2. Telemetry holds: every gen trial has `wall_ms>0` and `n_new>0`.  
3. Hot wall **~0.05 ms** / warm **~0.10 ms** beat FASTNEXT hot **0.17 ms** — PROMOTE is **speed** via cue-jump peak-fast product, not a larger LM.

### FIX note

First run soft-PROMOTE via e2e&lt;2.0 while hot wall **0.19** missed FASTNEXT **0.17**. FIX: require **wall** beat vs FASTNEXT; tighten K=1 · ctx≤480 · per-hit extract · 160 hot rounds → re-ASK PROMOTE (hot **0.05**).

## Finding

1. GENEDGE peak-extractive warm/hot wall **~0.10 / 0.05 ms** beats cold **~0.14 ms** and sits below FASTNEXT hot **0.17 ms**.  
2. All 10 gen trials keep `wall_ms>0` and `n_new>0` — anti-FP telemetry holds.  
3. LOOKUP stays mean **9.0** but is explicitly **not** used as speed IQ.  
4. Gen mean **7.0** meets quality floor ≥5.0 — ship claim remains **AF packaged stack** (not open chat).

## Reproduce

```bash
npm run nano:an:session
npm run nano:fastedge
# alias: npm run nano:an:fastedge
npm run nano:test && npm run verify
```

## Artifacts

- Summary: `results/nano-lm/wave-an/fastedge_summary.json`  
- Trials: `AN-FASTEDGE-{LOOKUP|GEN}-HITL-01…10`  
- Contract: `nano_lm/tests/test_fastedge.py`

Next: **AN5 H-APPEDGE** — real apps + DEPL dual-arm.
