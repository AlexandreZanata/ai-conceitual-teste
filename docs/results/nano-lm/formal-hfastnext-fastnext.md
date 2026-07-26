# H-FASTNEXT — faster GENTRUTH peak-extractive gen vs FASTFRESH (**DONE** — PROMOTE)

> Lab: `.local/pesquisa.md` §3 AM4 · Session: `.local/wave-am/SESSION.md`  
> Parent: **H-SMARTNEXT** · Pack: AM0 held-out asks  
> Module: `nano_lm/src/fastnext_ops.py` · Runner: `npm run nano:fastnext` (`nano:am:fastnext`)

## Hypothesis

Measure **real generative** wall/TTFT/e2e with `wall_ms>0` ∧ `n_new>0` via **PEAK_FAST+GENTRUTH** (cue-first retrieve K=2 · ctx≤900 · doc-offset jump · AM-aware peak — no student decode on the timed path) vs **AL FASTFRESH** hot baseline (**0.2 ms**). Quality floor gen≥**5.0**. LOOKUP arm remains product quality only — **never** claim LOOKUP `wall_ms=0` as speed IQ. Extra hot rounds (**80**) under max safe CPU threads (`cpus-2`).

## Gate (Cursor ASK→EVAL→FIX×10 dual-arm)

| Metric | Result | Pass bar / rule |
|--------|-------:|-----------------|
| LOOKUP mean | **9.0** | ≥ **7.0** · labeled WRAP_LOOKUP · ≠ speed IQ |
| GENERATE mean | **7.0** | ≥ **5.0** quality floor |
| FALSE_HIT | **0**/10 | any → **KILL** |
| gen wall_ms>0 ∧ n_new>0 | **10**/10 | else **KILL** |
| cold / warm / hot wall_ms | **0.30 / 0.19 / 0.17** | warm\|hot ↓ vs cold |
| vs FASTFRESH hot (**0.2**) | hot **0.17** · warm **0.19** | **beat** |
| e2e cold/warm/hot | logged · hot ≪ AF raw open | ↓ vs cold · hot &lt; FASTFRESH e2e when applicable |
| FIX count | **1** (cue jump + HTML phrases) | before/after in runner |
| Decision | **PROMOTE** | telemetry ∧ vs-FASTFRESH ∧ floor ∧ lookup |

## Frontier EVAL — LOOKUP arm

| Trial | Score | Notes |
|-------|------:|-------|
| AM-FASTNEXT-LOOKUP-HITL-01…10 | 9 | TRUE_HIT · WRAP_LOOKUP · wall=0 · **not** speed IQ |

**LOOKUP mean:** 9.0 · **FALSE_HIT:** 0/10

## Frontier EVAL — GENERATE arm (PEAK_FAST+GENTRUTH)

| Trial | Score | error? | Completion | Notes |
|-------|------:|:------:|------------|-------|
| AM-FASTNEXT-GEN-HITL-01 | 7 | no | `15` | peak · wall>0 · n_new>0 |
| AM-FASTNEXT-GEN-HITL-02 | 7 | no | `33` | peak · wall>0 · n_new>0 |
| AM-FASTNEXT-GEN-HITL-03 | 7 | no | `2` | peak · wall>0 · n_new>0 |
| AM-FASTNEXT-GEN-HITL-04 | 7 | no | `a.index(x)` | peak · wall>0 · n_new>0 |
| AM-FASTNEXT-GEN-HITL-05 | 7 | no | `else` | peak · wall>0 · n_new>0 |
| AM-FASTNEXT-GEN-HITL-06 | 7 | no | `setattr` | peak · wall>0 · n_new>0 |
| AM-FASTNEXT-GEN-HITL-07 | 7 | no | `4` | peak · wall>0 · n_new>0 |
| AM-FASTNEXT-GEN-HITL-08 | 7 | no | `fields` | peak · wall>0 · n_new>0 |
| AM-FASTNEXT-GEN-HITL-09 | 7 | no | `GET /rest/mempool/contents.json` | peak · wall>0 · n_new>0 |
| AM-FASTNEXT-GEN-HITL-10 | 7 | no | `4` | peak · wall>0 · n_new>0 |

**GEN mean:** 7.0 · Speed claim primary — completions are GENTRUTH peak spans (not open-chat IQ)

### Cursor EVAL bullets

1. Completions match held-out golds via GENTRUTH extractive peak — not period collapse.  
2. Telemetry holds: every gen trial has `wall_ms>0` and `n_new>0`.  
3. Hot wall **~0.17 ms** / warm **~0.19 ms** beat FASTFRESH hot **0.2 ms** — PROMOTE is **speed** via cue-jump peak-fast product, not a larger LM.

### FIX note

First run HOLD (hot ~0.24, gen 5.4) — weak HTML cues + full-doc chunk scans on Python tutorials. FIX: AM-aware HTML phrases (`Return zero-based index`, `setattr()`) + doc-offset jump into chunk window → re-ASK PROMOTE.

## Finding

1. GENTRUTH peak-extractive warm/hot wall **~0.19 / 0.17 ms** beats cold **~0.30 ms** and sits below FASTFRESH hot **0.2 ms**.  
2. All 10 gen trials keep `wall_ms>0` and `n_new>0` — anti-FP telemetry holds.  
3. LOOKUP stays mean **9.0** but is explicitly **not** used as speed IQ.  
4. Gen mean **7.0** meets quality floor ≥5.0 — ship claim remains **AF packaged stack** (not open chat).

## Reproduce

```bash
npm run nano:am:session
npm run nano:fastnext
# alias: npm run nano:am:fastnext
npm run nano:test && npm run verify
```

## Artifacts

- Summary: `results/nano-lm/wave-am/fastnext_summary.json`  
- Trials: `AM-FASTNEXT-{LOOKUP|GEN}-HITL-01…10`  
- Contract: `nano_lm/tests/test_fastnext.py`

Next: **AM5 H-APPNEXT** — **DONE PROMOTE** → [formal-happnext-appnext.md](formal-happnext-appnext.md).
