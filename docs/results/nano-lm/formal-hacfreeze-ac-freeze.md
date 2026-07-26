# AC-FREEZE — Wave AC lock (**DONE** — PROMOTE)

> Lab: `.local/pesquisa.md` §8.5 AC7 · Public note: [ac-freeze.md](ac-freeze.md)  
> After: [wave-ac-summary.md](wave-ac-summary.md) / [paper-lab-wave-ac.md](paper-lab-wave-ac.md)

## Hypothesis

After AC-REPORT, freeze Wave AC the same way AB-FREEZE locked AB: **outcomes stay**; **no Wave AD** without an explicit reopen agenda.

## Gate

| Check | Result |
|-------|--------|
| AC formals keep CTXPLUS…APPPLUS · HITL · REPORT **PROMOTE** | **ok** |
| `wave-ac-summary` · `paper-lab-wave-ac` · `ac-freeze` contain **COMPLETE** | **ok** |
| RECIPES + champion-card contain **H-CTXPLUS** · **H-APPPLUS** · **COMPLETE** | **ok** |
| ASKFAST/SEMWRAP known-ask smoke | **ok** |
| Decision | **PROMOTE** |

## Reproduce

```bash
npm run nano:ac:freeze
```

## Finding

1. Product claim stays scoped AC packaged apps on AB+AC spine.  
2. AC-FREEZE does **not** invent new serve/train hyps.  
3. Further research requires a new § in `.local/pesquisa.md`.

## Artifacts

- Module: `nano_lm/src/ac_freeze_ops.py` · Runner: `nano_lm/src/run_ac_freeze.py`
- Summary: `results/nano-lm/wave-ac/ac_freeze.json`
- Contract: `nano_lm/tests/test_ac_freeze.py`
