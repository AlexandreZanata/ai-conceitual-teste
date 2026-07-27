# AS-DUAL-HITL — product + gen gate (**DONE** — PROMOTE)

> Lab: `.local/pesquisa.md` §5 AS8 · Session: `.local/wave-as/SESSION.md`  
> Parent: [formal-hnanogen3-nanogen3.md](formal-hnanogen3-nanogen3.md)  
> Module: `nano_lm/src/as_dual_hitl_ops.py` · Runner: `npm run nano:as:dual-hitl`

## Hypothesis

Composite dual-arm HITL (ASKABSTAIN · SHIPUI · ADVSAFE · METRICS · PARAEXT2 · apps). Generative ship claim unlocks **only** if AS7 H-NANOGEN3 PROMOTE.

## Gate

| Pillar | Decision |
|--------|----------|
| H-ASKABSTAIN (core) | **PROMOTE** |
| H-SHIPUI (core) | **PROMOTE** |
| H-ADVSAFE (core) | **PROMOTE** |
| H-METRICS (core) | **PROMOTE** |
| H-PARAEXT2 (deepen) | **PROMOTE** |
| Apps known/howto/long-doc | **PASS** |
| AS7 H-NANOGEN3 | **HOLD** |
| Ship claim | `AF packaged stack + AQ product layer — not open chat LM` |
| Decision | **PROMOTE** |

## Apps LOOKUP smoke

| Surface | lookup_kind | modeui_line |
|---------|-------------|-------------|
| known-ask | **TRUE_HIT** | `mode=LOOKUP · wall_ms=0.0000 · n_new=0 · raw=WRAP_LOOKUP` |
| howto | **TRUE_HIT** | `mode=LOOKUP · wall_ms=0.0000 · n_new=0 · raw=WRAP_LOOKUP` |
| long-doc | **TRUE_HIT** | `mode=LOOKUP · wall_ms=0.0000 · n_new=0 · raw=WRAP_LOOKUP` |

## Finding

1. Live re-verify of AS1–AS6 product pillars under max safe CPU (`cpus-2`).  
2. Three app surfaces TRUE_HIT LOOKUP (product path).  
3. AS7 HOLD → generative / open-chat / mini-AGI claim stays locked.  
4. Soft deepen defects (PARAEXT2) → HOLD; all PROMOTE → product PROMOTE with gen locked.

## Reproduce

```bash
npm run nano:as:dual-hitl
npm run nano:z:ask -- --wrap --question "Write a short Python function named add that returns the sum of two integers a and b."
```

## Artifacts

- Summary: `results/nano-lm/wave-as/as_dual_hitl_summary.json`  
- Contract: `nano_lm/tests/test_as_dual_hitl.py`

## Claims

| Allowed | Forbidden |
|---------|-----------|
| AF packaged stack + AQ product layer | Open chat / mini-AGI |
| Product PROMOTE with gen locked | Generative unlock without AS7 |
| Mode-visible LOOKUP apps | LOOKUP-as-gen-IQ · Wave AT invent |

Next: **AS9 AS-REPORT** — **DONE PROMOTE** → [wave-as-summary.md](wave-as-summary.md) · [paper-lab-wave-as.md](paper-lab-wave-as.md). Next: **AS10 AS-FREEZE**.
