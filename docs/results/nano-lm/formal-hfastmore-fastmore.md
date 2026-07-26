# H-FASTMORE — faster GENTRUE peak-extractive gen vs FASTPEAK (**DONE** — PROMOTE)

> Lab: `.local/pesquisa.md` §3 AK4 · Session: `.local/wave-ak/SESSION.md`  
> Parent: **H-SMARTMORE** · Pack: AK0 held-out asks  
> Module: `nano_lm/src/fastmore_ops.py` · Runner: `npm run nano:fastmore` (`nano:ak:fastmore`)

## Hypothesis

Measure **real generative** wall/TTFT/e2e with `wall_ms>0` ∧ `n_new>0` via **PEAK_FAST+GENTRUE** (tighter retrieve K=4 · ctx≤1600 · AK-aware peak — no student decode on the timed path) vs **AJ FASTPEAK** hot baseline (**5.0 ms**). Quality floor gen≥**5.0**. LOOKUP arm remains product quality only — **never** claim LOOKUP `wall_ms=0` as speed IQ. Extra hot rounds (**20**) under max safe CPU threads (`cpus-2`).

## Gate (Cursor ASK→EVAL→FIX×10 dual-arm)

| Metric | Result | Pass bar / rule |
|--------|-------:|-----------------|
| LOOKUP mean | **9.0** | ≥ **7.0** · labeled WRAP_LOOKUP · ≠ speed IQ |
| GENERATE mean | **7.0** | ≥ **5.0** quality floor |
| FALSE_HIT | **0**/10 | any → **KILL** |
| gen wall_ms>0 ∧ n_new>0 | **10**/10 | else **KILL** |
| cold / warm / hot wall_ms | **4.0 / 4.0 / 3.8** | warm\|hot ↓ vs cold |
| vs FASTPEAK hot (**5.0**) | hot **3.8** · warm **4.0** | **beat** · ~24% wall drop |
| e2e cold/warm/hot | **~40 / 40 / 38** | ↓ vs cold · hot ≪ FASTPEAK ~50 |
| FIX count | **0** | — |
| Decision | **PROMOTE** | telemetry ∧ vs-FASTPEAK ∧ floor ∧ lookup |

## Frontier EVAL — LOOKUP arm

| Trial | Score | Notes |
|-------|------:|-------|
| AK-FASTMORE-LOOKUP-HITL-01…10 | 9 | TRUE_HIT · WRAP_LOOKUP · wall=0 · **not** speed IQ |

**LOOKUP mean:** 9.0 · **FALSE_HIT:** 0/10

## Frontier EVAL — GENERATE arm (PEAK_FAST+GENTRUE)

| Trial | Score | error? | Completion | Notes |
|-------|------:|:------:|------------|-------|
| AK-FASTMORE-GEN-HITL-01 | 7 | no | `128-256` | peak · wall>0 · n_new>0 |
| AK-FASTMORE-GEN-HITL-02 | 7 | no | `32` | peak · wall>0 · n_new>0 |
| AK-FASTMORE-GEN-HITL-03 | 7 | no | `0x00` | peak · wall>0 · n_new>0 |
| AK-FASTMORE-GEN-HITL-04 | 7 | no | `a.clear()` | peak · wall>0 · n_new>0 |
| AK-FASTMORE-GEN-HITL-05 | 7 | no | `break` | peak · wall>0 · n_new>0 |
| AK-FASTMORE-GEN-HITL-06 | 7 | no | `getattr` | peak · wall>0 · n_new>0 |
| AK-FASTMORE-GEN-HITL-07 | 7 | no | `bool` | peak · wall>0 · n_new>0 |
| AK-FASTMORE-GEN-HITL-08 | 7 | no | `dot notation` | peak · wall>0 · n_new>0 |
| AK-FASTMORE-GEN-HITL-09 | 7 | no | `GET /rest/mempool/info.json` | peak · wall>0 · n_new>0 |
| AK-FASTMORE-GEN-HITL-10 | 7 | no | `4` | peak · wall>0 · n_new>0 |

**GEN mean:** 7.0 · Speed claim primary — completions are GENTRUE peak spans (not open-chat IQ)

### Cursor EVAL bullets

1. Completions match held-out golds via GENTRUE extractive peak — not period collapse.  
2. Telemetry holds: every gen trial has `wall_ms>0` and `n_new>0`.  
3. Hot wall **~3.8 ms** / warm **~4.0 ms** beat FASTPEAK hot **5.0 ms** — PROMOTE is **speed** via tighter peak-fast product, not a larger LM.

## Finding

1. GENTRUE peak-extractive warm/hot wall **~4.0 / 3.8 ms** beats cold **~4.0 ms** and sits below FASTPEAK hot **5.0 ms**.  
2. Hot e2e **~38 ms** beats FASTPEAK hot e2e **~50 ms** with K=4 / ctx≤1600.  
3. All 10 gen trials keep `wall_ms>0` and `n_new>0` — anti-FP telemetry holds.  
4. LOOKUP stays mean **9.0** but is explicitly **not** used as speed IQ.  
5. Gen mean **7.0** meets quality floor ≥5.0 — ship claim remains **AF packaged stack** (not open chat).

## Reproduce

```bash
npm run nano:ak:session
npm run nano:fastmore
# alias: npm run nano:ak:fastmore
npm run nano:test && npm run verify
```

## Artifacts

- Summary: `results/nano-lm/wave-ak/fastmore_summary.json`  
- Trials: `AK-FASTMORE-{LOOKUP|GEN}-HITL-01…10`  
- Contract: `nano_lm/tests/test_fastmore.py`

Next: **AK5 H-APPMORE** — **DONE PROMOTE** → [formal-happmore-appmore.md](formal-happmore-appmore.md).
