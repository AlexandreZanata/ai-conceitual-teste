# AQ-PRODUCT-HITL — final product verify (**DONE** — PROMOTE)

> Lab: `.local/pesquisa.md` §5 AQ7 · Session: `.local/wave-aq/SESSION.md`  
> Parent: [formal-hnanogen-nanogen.md](formal-hnanogen-nanogen.md)  
> Module: `nano_lm/src/aq_product_hitl_ops.py` · Runner: `npm run nano:aq:product-hitl`

## Hypothesis

Composite product verify (paraphrase · adversary · apps · modes). Generative ship claim unlocks **only** if AQ6 H-NANOGEN PROMOTE.

## Gate

| Pillar | Decision |
|--------|----------|
| H-PARAHIT | **PROMOTE** |
| H-ADVFP | **PROMOTE** |
| H-MODEUI | **PROMOTE** |
| Apps known/howto/long-doc | **PASS** |
| AQ6 H-NANOGEN | **HOLD** |
| Ship claim | `AF packaged stack + AQ product layer — not open chat LM` |
| Decision | **PROMOTE** |

## Apps LOOKUP smoke

| Surface | lookup_kind | modeui_line |
|---------|-------------|-------------|
| known-ask | **TRUE_HIT** | `mode=LOOKUP · wall_ms=0.0000 · n_new=0 · raw=WRAP_LOOKUP` |
| howto | **TRUE_HIT** | `mode=LOOKUP · wall_ms=0.0000 · n_new=0 · raw=WRAP_LOOKUP` |
| long-doc | **TRUE_HIT** | `mode=LOOKUP · wall_ms=0.0000 · n_new=0 · raw=WRAP_LOOKUP` |

## Finding

1. Live re-verify of AQ1/AQ2/AQ5 under max safe CPU (`cpus-2`).  
2. Three app surfaces TRUE_HIT LOOKUP (product path).  
3. AQ6 HOLD → generative / open-chat / mini-AGI claim stays locked.

## Reproduce

```bash
npm run nano:aq:product-hitl
npm run nano:z:ask -- --wrap --question "Write a short Python function named add that returns the sum of two integers a and b."
```

## Artifacts

- Summary: `results/nano-lm/wave-aq/aq_product_hitl_summary.json`  
- Contract: `nano_lm/tests/test_aq_product_hitl.py`

## Claims

| Allowed | Forbidden |
|---------|-----------|
| AF packaged stack + AQ product layer | Open chat / mini-AGI |
| Product PROMOTE with AQ6 HOLD | Generative unlock without AQ6 |
| Mode-visible LOOKUP apps | LOOKUP-as-gen-IQ |

Next: **AQ9 AQ-FREEZE** — lock AQ outcomes (report landed: [wave-aq-summary.md](wave-aq-summary.md)).
