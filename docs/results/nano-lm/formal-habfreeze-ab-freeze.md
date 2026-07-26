# AB-FREEZE — Wave AB lock (**DONE** — PROMOTE)

> Lab: `.local/pesquisa.md` §8.4 · Public note: [ab-freeze.md](ab-freeze.md)  
> After: [wave-ab-summary.md](wave-ab-summary.md) / [paper-lab-wave-ab.md](paper-lab-wave-ab.md)

## Hypothesis

After AB-REPORT, freeze Wave AB the same way AA-FREEZE locked AA: **outcomes stay**; **no Wave AC** without an explicit reopen agenda.

## Gate

| Check | Result |
|-------|--------|
| AB formals keep SEMWRAP…REALAPP · HITL · REPORT **PROMOTE** | **ok** |
| `wave-ab-summary` · `paper-lab-wave-ab` · `ab-freeze` contain **COMPLETE** | **ok** |
| RECIPES + champion-card contain **H-ZWRAP** · **H-WRAPBANK** · **H-SEMWRAP** · **COMPLETE** | **ok** |
| ASKFAST/SEMWRAP known-ask smoke | **ok** |
| Decision | **PROMOTE** |

## Reproduce

```bash
npm run nano:ab:freeze
```

## Finding

1. Product claim stays scoped AB apps on wrap+bank spine.  
2. AB-FREEZE does **not** invent new serve/train hyps.  
3. Further research requires a new § in `.local/pesquisa.md`.

## Artifacts

- Module: `nano_lm/src/ab_freeze_ops.py` · Runner: `nano_lm/src/run_ab_freeze.py`
- Summary: `results/nano-lm/wave-ab/ab_freeze.json`
- Contract: `nano_lm/tests/test_ab_freeze.py`
