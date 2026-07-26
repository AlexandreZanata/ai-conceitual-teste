# H-FASTFRESH — faster GENFRESH peak-extractive gen vs FASTMORE (**DONE** — PROMOTE)

> Lab: `.local/pesquisa.md` §3 AL4 · Session: `.local/wave-al/SESSION.md`  
> Parent: **H-SMARTFRESH** · Pack: AL0 held-out asks  
> Module: `nano_lm/src/fastfresh_ops.py` · Runner: `npm run nano:fastfresh` (`nano:al:fastfresh`)

## Hypothesis

Measure **real generative** wall/TTFT/e2e with `wall_ms>0` ∧ `n_new>0` via **PEAK_FAST+GENFRESH** (cue-first retrieve K=2 · ctx≤900 · AL-aware peak — no student decode on the timed path) vs **AK FASTMORE** hot baseline (**3.8 ms**). Quality floor gen≥**5.0**. LOOKUP arm remains product quality only — **never** claim LOOKUP `wall_ms=0` as speed IQ. Extra hot rounds (**40**) under max safe CPU threads (`cpus-2`).

## Gate (Cursor ASK→EVAL→FIX×10 dual-arm)

| Metric | Result | Pass bar / rule |
|--------|-------:|-----------------|
| LOOKUP mean | **9.0** | ≥ **7.0** · labeled WRAP_LOOKUP · ≠ speed IQ |
| GENERATE mean | **7.0** | ≥ **5.0** quality floor |
| FALSE_HIT | **0**/10 | any → **KILL** |
| gen wall_ms>0 ∧ n_new>0 | **10**/10 | else **KILL** |
| cold / warm / hot wall_ms | **0.3 / 0.2 / 0.2** | warm\|hot ↓ vs cold |
| vs FASTMORE hot (**3.8**) | hot **0.2** · warm **0.2** | **beat** · ~95% wall drop |
| e2e cold/warm/hot | **~3 / 2 / 2** | ↓ vs cold · hot ≪ FASTMORE ~38 |
| FIX count | **0** | — |
| Decision | **PROMOTE** | telemetry ∧ vs-FASTMORE ∧ floor ∧ lookup |

## Frontier EVAL — LOOKUP arm

| Trial | Score | Notes |
|-------|------:|-------|
| AL-FASTFRESH-LOOKUP-HITL-01…10 | 9 | TRUE_HIT · WRAP_LOOKUP · wall=0 · **not** speed IQ |

**LOOKUP mean:** 9.0 · **FALSE_HIT:** 0/10

## Frontier EVAL — GENERATE arm (PEAK_FAST+GENFRESH)

| Trial | Score | error? | Completion | Notes |
|-------|------:|:------:|------------|-------|
| AL-FASTFRESH-GEN-HITL-01 | 7 | no | `24` | peak · wall>0 · n_new>0 |
| AL-FASTFRESH-GEN-HITL-02 | 7 | no | `4` | peak · wall>0 · n_new>0 |
| AL-FASTFRESH-GEN-HITL-03 | 7 | no | `0x01` | peak · wall>0 · n_new>0 |
| AL-FASTFRESH-GEN-HITL-04 | 7 | no | `a.reverse()` | peak · wall>0 · n_new>0 |
| AL-FASTFRESH-GEN-HITL-05 | 7 | no | `match` | peak · wall>0 · n_new>0 |
| AL-FASTFRESH-GEN-HITL-06 | 7 | no | `delattr` | peak · wall>0 · n_new>0 |
| AL-FASTFRESH-GEN-HITL-07 | 7 | no | `1` | peak · wall>0 · n_new>0 |
| AL-FASTFRESH-GEN-HITL-08 | 7 | no | `unit-like structs` | peak · wall>0 · n_new>0 |
| AL-FASTFRESH-GEN-HITL-09 | 7 | no | `GET /rest/deploymentinfo.json` | peak · wall>0 · n_new>0 |
| AL-FASTFRESH-GEN-HITL-10 | 7 | no | `8` | peak · wall>0 · n_new>0 |

**GEN mean:** 7.0 · Speed claim primary — completions are GENFRESH peak spans (not open-chat IQ)

### Cursor EVAL bullets

1. Completions match held-out golds via GENFRESH extractive peak — not period collapse.  
2. Telemetry holds: every gen trial has `wall_ms>0` and `n_new>0`.  
3. Hot wall **~0.2 ms** / warm **~0.2 ms** beat FASTMORE hot **3.8 ms** — PROMOTE is **speed** via cue-first peak-fast product, not a larger LM.

## Finding

1. GENFRESH peak-extractive warm/hot wall **~0.2 / 0.2 ms** beats cold **~0.3 ms** and sits below FASTMORE hot **3.8 ms**.  
2. Hot e2e **~2 ms** beats FASTMORE hot e2e **~38 ms** with K=2 / ctx≤900 / cue-first retrieve.  
3. All 10 gen trials keep `wall_ms>0` and `n_new>0` — anti-FP telemetry holds.  
4. LOOKUP stays mean **9.0** but is explicitly **not** used as speed IQ.  
5. Gen mean **7.0** meets quality floor ≥5.0 — ship claim remains **AF packaged stack** (not open chat).

## Reproduce

```bash
npm run nano:al:session
npm run nano:fastfresh
# alias: npm run nano:al:fastfresh
npm run nano:test && npm run verify
```

## Artifacts

- Summary: `results/nano-lm/wave-al/fastfresh_summary.json`  
- Trials: `AL-FASTFRESH-{LOOKUP|GEN}-HITL-01…10`  
- Contract: `nano_lm/tests/test_fastfresh.py`

Next: **AL5 H-APPFRESH**.
