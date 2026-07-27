# H-NANOGEN — ablated generative gate (**DONE** — HOLD)

> Lab: `.local/pesquisa.md` §5 AQ6 · Session: `.local/wave-aq/SESSION.md`  
> Parent: [formal-hmodeui-modeui.md](formal-hmodeui-modeui.md) · Baseline: [formal-hgenbase-genbase.md](formal-hgenbase-genbase.md)  
> Module: `nano_lm/src/nanogen_ops.py` · Runner: `npm run nano:nanogen`

## Hypothesis

North-star **ablated DECODE** on **held-out + paraphrase** (n=10). PROMOTE only if ablated mean ≥ **5.0**; else honest **HOLD** (peak compare only).

## Gate

| Metric | Result | Pass bar |
|--------|-------:|----------|
| LOOKUP mean | **9.0** | ≥ 7.0 |
| GENERATE ablated mean | **4.0** | ≥ 5.0 for PROMOTE |
| GENERATE peak_on mean | **6.5** | compare only |
| peak_only_lift | **True** | peak≥5 ∧ ablated<5 → HOLD |
| FALSE_HIT | **0**/10 | any → KILL |
| Decision | **HOLD** | — |

## Pack

- 5× AP0 held-out (`AP-HITL-*`)  
- 5× AQ0 paraphrase (`AQ-PARA-*` ask text = paraphrase)  
- Gate scores **ablated** arm only; peak is anti-FP compare.

## Finding

1. Dual-arm LOOKUP + ablated DECODE under max safe CPU (`cpus-2`).  
2. Generative ship language lifts **only** on ablated PROMOTE.  
3. Peak extractive lift alone → HOLD (not open-chat IQ).

## Reproduce

```bash
npm run nano:nanogen
npm run nano:z:ask -- --question "Human rewrite: make a small Python function add(a, b) that returns a plus b."
```

## Artifacts

- Summary: `results/nano-lm/wave-aq/nanogen_summary.json`  
- Contract: `nano_lm/tests/test_nanogen.py`

## Claims

| Allowed | Forbidden |
|---------|-----------|
| Honest HOLD on ablated <5 | LOOKUP-as-gen-IQ |
| Peak compare labeled | Peak-as-open-chat |
| PROMOTE only ablated≥5 | Wave AR invent |

Next: **AQ7 AQ-PRODUCT-HITL** — **DONE PROMOTE** → [wave-aq-product-hitl.md](wave-aq-product-hitl.md).
