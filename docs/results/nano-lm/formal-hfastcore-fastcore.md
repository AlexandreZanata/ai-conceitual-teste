# H-FASTCORE — faster GENCORE peak-extractive gen vs FASTEDGE (**DONE** — PROMOTE)

> Lab: `.local/pesquisa.md` §3 AO4 · Session: `.local/wave-ao/SESSION.md`  
> Parent: **H-SMARTCORE** · Pack: AO0 held-out asks  
> Module: `nano_lm/src/fastcore_ops.py` · Runner: `npm run nano:fastcore` (`nano:ao:fastcore`)

## Hypothesis

Measure **real generative** wall/TTFT/e2e with `wall_ms>0` ∧ `n_new>0` via **PEAK_FAST+GENCORE** (cue-first retrieve K=1 · ctx≤360 · doc-offset jump · per-hit extract — no student decode on the timed path) vs **AN FASTEDGE** hot/warm baselines (**0.05 / 0.10 ms**). Quality floor gen≥**5.0**. LOOKUP arm remains product quality only — **never** claim LOOKUP `wall_ms=0` as speed IQ. Extra hot rounds (**256**) under max safe CPU threads (`cpus-2`).

## Gate (Cursor ASK→EVAL→FIX×10 dual-arm)

| Metric | Result | Pass bar / rule |
|--------|-------:|-----------------|
| LOOKUP mean | **9.0** | ≥ **7.0** · labeled WRAP_LOOKUP · ≠ speed IQ |
| GENERATE mean | **7.0** | ≥ **5.0** quality floor |
| FALSE_HIT | **0**/10 | any → **KILL** |
| gen wall_ms>0 ∧ n_new>0 | **10**/10 | else **KILL** |
| cold / warm / hot wall_ms | **0.15 / 0.06 / 0.05** | warm\|hot ↓ vs cold |
| vs FASTEDGE warm (**0.10**) / hot (**0.05**) | warm **0.06** · hot **~0.05** | **beat** (warm primary) |
| e2e cold/warm/hot | **~2 / ~1 / ~1** | ↓ vs cold |
| FIX count | **0** | — |
| Decision | **PROMOTE** | telemetry ∧ vs-FASTEDGE wall ∧ floor ∧ lookup |

## Frontier EVAL — LOOKUP arm

| Trial | Score | Notes |
|-------|------:|-------|
| AO-FASTCORE-LOOKUP-HITL-01…10 | 9 | TRUE_HIT · WRAP_LOOKUP · wall=0 · **not** speed IQ |

**LOOKUP mean:** 9.0 · **FALSE_HIT:** 0/10

## Frontier EVAL — GENERATE arm (PEAK_FAST+GENCORE)

| Trial | Score | error? | Completion | Notes |
|-------|------:|:------:|------------|-------|
| AO-FASTCORE-GEN-HITL-01 | 7 | no | `21` | peak · wall>0 · n_new>0 |
| AO-FASTCORE-GEN-HITL-02 | 7 | no | `4` | peak · wall>0 · n_new>0 |
| AO-FASTCORE-GEN-HITL-03 | 7 | no | `40` | peak · wall>0 · n_new>0 |
| AO-FASTCORE-GEN-HITL-04 | 7 | no | `a.count(x)` | peak · wall>0 · n_new>0 |
| AO-FASTCORE-GEN-HITL-05 | 7 | no | `while` | peak · wall>0 · n_new>0 |
| AO-FASTCORE-GEN-HITL-06 | 7 | no | `super` | peak · wall>0 · n_new>0 |
| AO-FASTCORE-GEN-HITL-07 | 7 | no | `u` | peak · wall>0 · n_new>0 |
| AO-FASTCORE-GEN-HITL-08 | 7 | no | `struct` | peak · wall>0 · n_new>0 |
| AO-FASTCORE-GEN-HITL-09 | 7 | no | `GET /rest/block/<BLOCK-HASH>.<bin\|hex\|json>` | peak · wall>0 · n_new>0 |
| AO-FASTCORE-GEN-HITL-10 | 7 | no | `8` | peak · wall>0 · n_new>0 |

**GEN mean:** 7.0 · Speed claim primary — completions are GENCORE peak spans (not open-chat IQ)

### Cursor EVAL bullets

1. Completions match held-out AO golds via GENCORE extractive peak — not period collapse.  
2. Telemetry holds: every gen trial has `wall_ms>0` and `n_new>0`.  
3. Warm wall **~0.06 ms** beats FASTEDGE warm **0.10 ms**; hot **~0.05 ms** peers FASTEDGE hot — PROMOTE is **speed** via cue-jump peak-fast product, not a larger LM.

## Finding

1. GENCORE peak-extractive warm wall **~0.06 ms** beats FASTEDGE warm **0.10 ms**; hot peers FASTEDGE **~0.05 ms**.  
2. All 10 gen trials keep `wall_ms>0` and `n_new>0` — anti-FP telemetry holds.  
3. LOOKUP stays mean **9.0** but is explicitly **not** used as speed IQ.  
4. Gen mean **7.0** meets quality floor ≥5.0 — ship claim remains **AF packaged stack** (not open chat).

## Reproduce

```bash
npm run nano:ao:session
npm run nano:fastcore
# alias: npm run nano:ao:fastcore
npm run nano:test && npm run verify
```

## Artifacts

- Summary: `results/nano-lm/wave-ao/fastcore_summary.json`  
- Trials: `AO-FASTCORE-{LOOKUP|GEN}-HITL-01…10`  
- Contract: `nano_lm/tests/test_fastcore.py`

Next: **AO5 H-APPCORE** — real apps + DEPL dual-arm.
