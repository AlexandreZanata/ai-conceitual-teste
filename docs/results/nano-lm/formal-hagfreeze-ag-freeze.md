# AG-FREEZE — Wave AG lock (**DONE** — PROMOTE)

> Lab: `.local/pesquisa.md` §5 AG8 · Public note: [ag-freeze.md](ag-freeze.md)  
> After: [wave-ag-summary.md](wave-ag-summary.md) / [paper-lab-wave-ag.md](paper-lab-wave-ag.md)

## Hypothesis

After AG-REPORT, freeze Wave AG the same way AF-FREEZE locked AF: **outcomes stay** (including honest HOLDs); **no Wave AH** without an explicit reopen agenda.

## Gate

| Check | Result |
|-------|--------|
| AG formals keep ANTIFP…APPREAL · HITL · REPORT decisions | **ok** |
| `wave-ag-summary` · `paper-lab-wave-ag` · `ag-freeze` contain **COMPLETE** | **ok** |
| RECIPES + champion-card contain **H-ANTIFP** · **AG-HITL-10** · **COMPLETE** | **ok** |
| Dual-arm LOOKUP+GENERATE smoke (`wall_ms>0`) | **ok** |
| Decision | **PROMOTE** |

## Reproduce

```bash
npm run nano:ag:freeze
```

## Finding

1. Ship claim stays scoped **AF packaged stack** (AG gen arm below bar).  
2. AG-FREEZE does **not** invent new serve/train hyps.  
3. Further research requires a new § in `.local/pesquisa.md` (Wave AH reopen).  
4. Anti-FP law remains: LOOKUP ≠ generative IQ.

## Artifacts

- Module: `nano_lm/src/ag_freeze_ops.py` · Runner: `nano_lm/src/run_ag_freeze.py`
- Summary: `results/nano-lm/wave-ag/ag_freeze.json`
- Contract: `nano_lm/tests/test_ag_freeze.py`
