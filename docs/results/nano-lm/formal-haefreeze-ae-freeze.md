# AE-FREEZE — Wave AE lock (**DONE** — PROMOTE)

> Lab: `.local/pesquisa.md` §5 AE7 · Public note: [ae-freeze.md](ae-freeze.md)  
> After: [wave-ae-summary.md](wave-ae-summary.md) / [paper-lab-wave-ae.md](paper-lab-wave-ae.md)

## Hypothesis

After AE-REPORT, freeze Wave AE the same way AD-FREEZE locked AD: **outcomes stay**; **no Wave AF** without an explicit reopen agenda.

## Gate

| Check | Result |
|-------|--------|
| AE formals keep CTXMAX…APPMAX · HITL · REPORT **PROMOTE** | **ok** |
| `wave-ae-summary` · `paper-lab-wave-ae` · `ae-freeze` contain **COMPLETE** | **ok** |
| RECIPES + champion-card contain **H-CTXMAX** · **AE-HITL-10** · **COMPLETE** | **ok** |
| ASKFAST/SEMWRAP held-out known-ask smoke | **ok** |
| Decision | **PROMOTE** |

## Reproduce

```bash
npm run nano:ae:freeze
```

## Finding

1. Product claim stays scoped AE packaged stack (CTXMAX+SMARTMAX+FASTMAX+APPMAX).  
2. AE-FREEZE does **not** invent new serve/train hyps.  
3. Further research requires a new § in `.local/pesquisa.md`.

## Artifacts

- Module: `nano_lm/src/ae_freeze_ops.py` · Runner: `nano_lm/src/run_ae_freeze.py`
- Summary: `results/nano-lm/wave-ae/ae_freeze.json`
- Contract: `nano_lm/tests/test_ae_freeze.py`
