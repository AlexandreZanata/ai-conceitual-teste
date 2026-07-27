# AR-DUAL-HITL — product + gen gate (**DONE** — HOLD (product soft: paraext:HOLD,advreg:KILL))

> Lab: `.local/pesquisa.md` §5 AR6 · Session: `.local/wave-ar/SESSION.md`  
> Parent: [formal-hnanogen2-nanogen2.md](formal-hnanogen2-nanogen2.md)  
> Module: `nano_lm/src/ar_dual_hitl_ops.py` · Runner: `npm run nano:ar:dual-hitl`

## Hypothesis

Composite dual-arm HITL (ABSTAIN · SHIPDEMO · PARAEXT · ADVREG · apps). Generative ship claim unlocks **only** if AR5 H-NANOGEN2 PROMOTE.

## Gate

| Pillar | Decision |
|--------|----------|
| H-ABSTAIN (core) | **PROMOTE** |
| H-SHIPDEMO (core) | **PROMOTE** |
| H-PARAEXT (deepen) | **HOLD** |
| H-ADVREG (deepen) | **KILL** |
| Apps known/howto/long-doc | **PASS** |
| AR5 H-NANOGEN2 | **HOLD** |
| Ship claim | `AF packaged stack + AQ product layer — not open chat LM` |
| Decision | **HOLD (product soft: paraext:HOLD,advreg:KILL)** |

## Apps LOOKUP smoke

| Surface | lookup_kind | modeui_line |
|---------|-------------|-------------|
| known-ask | **TRUE_HIT** | `mode=LOOKUP · wall_ms=0.0000 · n_new=0 · raw=WRAP_LOOKUP` |
| howto | **TRUE_HIT** | `mode=LOOKUP · wall_ms=0.0000 · n_new=0 · raw=WRAP_LOOKUP` |
| long-doc | **TRUE_HIT** | `mode=LOOKUP · wall_ms=0.0000 · n_new=0 · raw=WRAP_LOOKUP` |

## Finding

1. Live re-verify of AR1–AR4 under max safe CPU (`cpus-2`).  
2. Three app surfaces TRUE_HIT LOOKUP (product path).  
3. AR5 HOLD → generative / open-chat / mini-AGI claim stays locked.  
4. Soft deepen defects (PARAEXT/ADVREG) → HOLD, not silent PROMOTE.

## Reproduce

```bash
npm run nano:ar:dual-hitl
npm run nano:z:ask -- --wrap --question "Write a short Python function named add that returns the sum of two integers a and b."
```

## Artifacts

- Summary: `results/nano-lm/wave-ar/ar_dual_hitl_summary.json`  
- Contract: `nano_lm/tests/test_ar_dual_hitl.py`

## Claims

| Allowed | Forbidden |
|---------|-----------|
| AF packaged stack + AQ product layer | Open chat / mini-AGI |
| Product HOLD with soft deepen defects | Generative unlock without AR5 |
| Mode-visible LOOKUP apps | LOOKUP-as-gen-IQ · Wave AS invent |

Next: **AR7 AR-REPORT** — **DONE PROMOTE** → [wave-ar-summary.md](wave-ar-summary.md) · [paper-lab-wave-ar.md](paper-lab-wave-ar.md). **AR8 AR-FREEZE** — **DONE PROMOTE** → [ar-freeze.md](ar-freeze.md). Do not invent Wave AS.
