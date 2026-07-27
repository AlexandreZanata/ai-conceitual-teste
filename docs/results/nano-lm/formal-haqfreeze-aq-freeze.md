# AQ-FREEZE — Wave AQ lock (**DONE** — PROMOTE)

> Lab: `.local/pesquisa.md` §5 AQ9 · Public note: [aq-freeze.md](aq-freeze.md)  
> After: [wave-aq-summary.md](wave-aq-summary.md) / [paper-lab-wave-aq.md](paper-lab-wave-aq.md)

## Hypothesis

After AQ-REPORT, freeze Wave AQ the same way AP-FREEZE locked AP: **outcomes stay** (product PROMOTEs + H-NANOGEN HOLD); **no Wave AR** without an explicit reopen agenda.

## Gate

| Check | Result |
|-------|--------|
| AQ formals keep PARAHIT…MODEUI · NANOGEN HOLD · HITL · REPORT decisions | **ok** |
| `wave-aq-summary` · `paper-lab-wave-aq` · `aq-freeze` contain **COMPLETE** | **ok** |
| RECIPES + champion-card contain **H-PARAHIT** · **AQ-PRODUCT-HITL** · **COMPLETE** | **ok** |
| LOOKUP·PEAK·DECODE mode triad smoke | **ok** |
| Decision | **PROMOTE** |

## Reproduce

```bash
npm run nano:aq:freeze
```

## Finding

1. Ship claim stays scoped **AF packaged stack + AQ product layer — not open chat LM**.  
2. AQ-FREEZE does **not** invent new serve/train hyps.  
3. Further research requires a new § in `.local/pesquisa.md` (Wave AR reopen).  
4. Anti-FP law remains: LOOKUP ≠ generative IQ; PEAK ≠ open-chat IQ; H-NANOGEN HOLD locks gen claim.  
5. ≤5M hard law remains (CAPCHECK closed).

## Artifacts

- Module: `nano_lm/src/aq_freeze_ops.py` · Runner: `nano_lm/src/run_aq_freeze.py`
- Summary: `results/nano-lm/wave-aq/aq_freeze.json`
- Contract: `nano_lm/tests/test_aq_freeze.py`
