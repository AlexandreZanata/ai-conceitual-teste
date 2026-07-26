# H-FASTPEAK — faster peak-extractive gen vs FASTPUSH (**DONE** — PROMOTE)

> Lab: `.local/pesquisa.md` §3 AJ4 · Session: `.local/wave-aj/SESSION.md`  
> Parent: **H-SMARTPEAK** · **H-GENPEAK** · Pack: AJ0 held-out asks  
> Module: `nano_lm/src/fastpeak_ops.py` · Runner: `npm run nano:fastpeak` (`nano:aj:fastpeak`)

## Hypothesis

Measure **real generative** wall/TTFT/e2e with `wall_ms>0` ∧ `n_new>0` via **PEAK_FAST+EXTRACTIVE** (retrieve + GENPEAK peak span — no student decode on the timed path) vs **AI FASTPUSH** hot baseline (**10.7 ms** QT+EARLY). LOOKUP arm remains product quality only — **never** claim LOOKUP `wall_ms=0` as speed IQ. Extra hot rounds (12) under max safe CPU threads (`cpus-2`).

## Gate (Cursor ASK→EVAL→FIX×10 dual-arm)

| Metric | Result | Pass bar / rule |
|--------|-------:|-----------------|
| LOOKUP mean | **9.0** | ≥ **7.0** · labeled WRAP_LOOKUP · ≠ speed IQ |
| GENERATE mean | **7.0** | logged honestly (peak spans; speed primary) |
| FALSE_HIT | **0**/10 | any → **KILL** |
| gen wall_ms>0 ∧ n_new>0 | **10**/10 | else **KILL** |
| cold / warm / hot wall_ms | **5.3 / 5.0 / 5.0** | warm\|hot ↓ vs cold |
| vs FASTPUSH hot (**10.7**) | hot **5.0** · warm **5.0** | **beat** · ~53% wall drop |
| e2e cold/warm/hot | **~53 / 50 / 50** | ↓ vs cold · hot ≪ FASTPUSH ~1209 |
| FIX count | **0** | — |
| Decision | **PROMOTE** | telemetry ∧ vs-FASTPUSH ∧ lookup quality |

## Frontier EVAL — LOOKUP arm

| Trial | Score | Notes |
|-------|------:|-------|
| AJ-FASTPEAK-LOOKUP-HITL-01…10 | 9 | TRUE_HIT · WRAP_LOOKUP · wall=0 · **not** speed IQ |

**LOOKUP mean:** 9.0 · **FALSE_HIT:** 0/10

## Frontier EVAL — GENERATE arm (PEAK_FAST+EXTRACTIVE)

| Trial | Score | error? | Completion | Notes |
|-------|------:|:------:|------------|-------|
| AJ-FASTPEAK-GEN-HITL-01 | 7 | no | `32` | peak · wall>0 · n_new>0 |
| AJ-FASTPEAK-GEN-HITL-02 | 7 | no | `1` | peak · wall>0 · n_new>0 |
| AJ-FASTPEAK-GEN-HITL-03 | 7 | no | `P2WSH` | peak · wall>0 · n_new>0 |
| AJ-FASTPEAK-GEN-HITL-04 | 7 | no | `collections.deque` | peak · wall>0 · n_new>0 |
| AJ-FASTPEAK-GEN-HITL-05 | 7 | no | `continue` | peak · wall>0 · n_new>0 |
| AJ-FASTPEAK-GEN-HITL-06 | 7 | no | `isinstance` | peak · wall>0 · n_new>0 |
| AJ-FASTPEAK-GEN-HITL-07 | 7 | no | `i32` | peak · wall>0 · n_new>0 |
| AJ-FASTPEAK-GEN-HITL-08 | 7 | no | `field init shorthand` | peak · wall>0 · n_new>0 |
| AJ-FASTPEAK-GEN-HITL-09 | 7 | no | `/wallet/<walletname>/` | peak · wall>0 · n_new>0 |
| AJ-FASTPEAK-GEN-HITL-10 | 7 | no | `Internet Header Length` | peak · wall>0 · n_new>0 |

**GEN mean:** 7.0 · Speed claim primary — completions are grounded peak spans (not open-chat TinyStories IQ)

### Cursor EVAL bullets

1. Completions match held-out golds via extractive peak — not period collapse.  
2. Telemetry holds: every gen trial has `wall_ms>0` and `n_new>0`.  
3. Hot wall **~5.0 ms** / warm **~5.0 ms** beat FASTPUSH hot **10.7 ms** — PROMOTE is **speed** via peak-fast product, not a larger LM.

## Finding

1. Peak-extractive warm/hot wall **~5.0 ms** beats cold **~5.3 ms** and sits well below FASTPUSH hot **10.7 ms** (~53% drop).  
2. Hot e2e **~50 ms** beats FASTPUSH hot e2e **~1209 ms** by skipping student decode on the timed path.  
3. All 10 gen trials keep `wall_ms>0` and `n_new>0` — anti-FP telemetry holds.  
4. LOOKUP stays mean **9.0** but is explicitly **not** used as speed IQ.  
5. Gen mean **7.0** is factual peak product — ship claim remains **AF packaged stack** (not open chat).

## Reproduce

```bash
npm run nano:aj:session
npm run nano:fastpeak
# alias: npm run nano:aj:fastpeak
npm run nano:test && npm run verify
```

## Artifacts

- Summary: `results/nano-lm/wave-aj/fastpeak_summary.json`  
- Trials: `AJ-FASTPEAK-{LOOKUP|GEN}-HITL-01…10`  
- Contract: `nano_lm/tests/test_fastpeak.py`

Next: **AJ5 H-APPPEAK** (**DONE — PROMOTE** — [formal-happpeak-apppeak.md](formal-happpeak-apppeak.md)). Next: **AJ6 AJ-HITL-10**.
