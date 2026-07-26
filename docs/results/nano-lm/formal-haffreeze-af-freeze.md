# AF-FREEZE — Wave AF lock (**DONE** — PROMOTE)

> Lab: `.local/pesquisa.md` §5 AF7 · Public note: [af-freeze.md](af-freeze.md)  
> After: [wave-af-summary.md](wave-af-summary.md) / [paper-lab-wave-af.md](paper-lab-wave-af.md)

## Hypothesis

After AF-REPORT, freeze Wave AF the same way AE-FREEZE locked AE: **outcomes stay**; **no Wave AG** without an explicit reopen agenda.

## Gate

| Check | Result |
|-------|--------|
| AF formals keep CTXULTRA…APPULTRA · HITL · REPORT **PROMOTE** | **ok** |
| `wave-af-summary` · `paper-lab-wave-af` · `af-freeze` contain **COMPLETE** | **ok** |
| RECIPES + champion-card contain **H-CTXULTRA** · **AF-HITL-10** · **COMPLETE** | **ok** |
| ASKFAST/SEMWRAP held-out known-ask smoke | **ok** |
| Decision | **PROMOTE** |

## Reproduce

```bash
npm run nano:af:freeze
```

## Finding

1. Product claim stays scoped AF packaged stack (CTXULTRA+SMARTULTRA+FASTULTRA+APPULTRA).  
2. AF-FREEZE does **not** invent new serve/train hyps.  
3. Further research requires a new § in `.local/pesquisa.md`.

## Artifacts

- Module: `nano_lm/src/af_freeze_ops.py` · Runner: `nano_lm/src/run_af_freeze.py`
- Summary: `results/nano-lm/wave-af/af_freeze.json`
- Contract: `nano_lm/tests/test_af_freeze.py`
