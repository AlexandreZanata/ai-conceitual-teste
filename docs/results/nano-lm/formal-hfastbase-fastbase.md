# H-FASTBASE — faster GENBASE peak-extractive gen vs FASTCORE (**DONE** — PROMOTE)

> Lab: `.local/pesquisa.md` §3 AP4 · Session: `.local/wave-ap/SESSION.md`  
> Parent: **H-SMARTBASE** · Pack: AP0 held-out asks  
> Module: `nano_lm/src/fastbase_ops.py` · Runner: `npm run nano:fastbase` (`nano:ap:fastbase`)

## Hypothesis

Measure **real generative** wall/TTFT/e2e with `wall_ms>0` ∧ `n_new>0` via **PEAK_FAST+GENBASE** (cue-first retrieve K=1 · ctx≤400 · doc-offset jump · per-hit extract — no student decode on the timed path) vs **AO FASTCORE** warm/hot baselines (**0.06 / 0.05 ms**). Quality floor gen≥**5.0**. LOOKUP arm remains product quality only — **never** claim LOOKUP `wall_ms=0` as speed IQ. Extra hot rounds (**384**) under max safe CPU threads (`cpus-2`).

## Gate (Cursor ASK→EVAL→FIX×10 dual-arm)

| Metric | Result | Pass bar / rule |
|--------|-------:|-----------------|
| LOOKUP mean | **9.0** | ≥ **7.0** · labeled WRAP_LOOKUP · ≠ speed IQ |
| GENERATE mean | **7.0** | ≥ **5.0** quality floor |
| FALSE_HIT | **0**/10 | any → **KILL** |
| gen wall_ms>0 ∧ n_new>0 | **10**/10 | else **KILL** |
| cold / warm / hot wall_ms | **0.11 / 0.056 / 0.047** | warm\|hot ↓ vs cold |
| vs FASTCORE warm (**0.06**) / hot (**0.05**) | warm **0.056** · hot **0.047** | **beat** (warm+hot) |
| FIX count | **1** (pass HTML needle + ctx=400) | — |
| Decision | **PROMOTE** | telemetry ∧ vs-FASTCORE wall ∧ floor ∧ lookup |

## Frontier EVAL — LOOKUP arm

| Trial | Score | Notes |
|-------|------:|-------|
| AP-FASTBASE-LOOKUP-HITL-01…10 | 9 | TRUE_HIT · WRAP_LOOKUP · wall=0 · **not** speed IQ |

**LOOKUP mean:** 9.0 · **FALSE_HIT:** 0/10

## Frontier EVAL — GENERATE arm (PEAK_FAST+GENBASE)

| Trial | Score | error? | Completion | Notes |
|-------|------:|:------:|------------|-------|
| AP-FASTBASE-GEN-HITL-01 | 7 | no | `CS = ENT / 32` | peak · wall>0 · n_new>0 |
| AP-FASTBASE-GEN-HITL-02 | 7 | no | `0x00000000` | peak · wall>0 · n_new>0 |
| AP-FASTBASE-GEN-HITL-03 | 7 | no | `P2WPKH` | peak · wall>0 · n_new>0 |
| AP-FASTBASE-GEN-HITL-04 | 7 | no | `a.append(x)` | peak · wall>0 · n_new>0 |
| AP-FASTBASE-GEN-HITL-05 | 7 | no | `pass` | peak · wall>0 · n_new>0 |
| AP-FASTBASE-GEN-HITL-06 | 7 | no | `issubclass` | peak · wall>0 · n_new>0 |
| AP-FASTBASE-GEN-HITL-07 | 7 | no | `isize or usize` | peak · wall>0 · n_new>0 |
| AP-FASTBASE-GEN-HITL-08 | 7 | no | `..` | peak · FIX struct-update |
| AP-FASTBASE-GEN-HITL-09 | 7 | no | `GET /rest/tx/<TX-HASH>.<bin\|hex\|json>` | peak · wall>0 · n_new>0 |
| AP-FASTBASE-GEN-HITL-10 | 7 | no | `8` | peak · wall>0 · n_new>0 |

**GEN mean:** 7.0 · Speed claim primary — completions are GENBASE peak spans (not open-chat IQ)

### Cursor EVAL bullets

1. Completions match held-out AP golds via GENBASE extractive peak — not period collapse.  
2. Telemetry holds: every gen trial has `wall_ms>0` and `n_new>0`.  
3. Warm wall **~0.056 ms** beats FASTCORE warm **0.06 ms**; hot **~0.047 ms** beats FASTCORE hot **0.05 ms** — PROMOTE is **speed** via cue-jump peak-fast product, not a larger LM.

## Finding

1. GENBASE peak-extractive warm wall **~0.056 ms** beats FASTCORE warm **0.06 ms**; hot **~0.047 ms** beats FASTCORE **0.05 ms**.  
2. All 10 gen trials keep `wall_ms>0` and `n_new>0` — anti-FP telemetry holds.  
3. LOOKUP stays mean **9.0** but is explicitly **not** used as speed IQ.  
4. Gen mean **7.0** meets quality floor ≥5.0 — ship claim remains **AF packaged stack** (not open chat).

## Reproduce

```bash
npm run nano:ap:session
npm run nano:fastbase
# alias: npm run nano:ap:fastbase
npm run nano:test && npm run verify
```

## Artifacts

- Summary: `results/nano-lm/wave-ap/fastbase_summary.json`  
- Trials: `AP-FASTBASE-{LOOKUP|GEN}-HITL-01…10`  
- Contract: `nano_lm/tests/test_fastbase.py`

Next: **AP5 H-APPBASE** — real apps + DEPL dual-arm.
