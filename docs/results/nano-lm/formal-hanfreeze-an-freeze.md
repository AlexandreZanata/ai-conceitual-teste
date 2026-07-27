# AN-FREEZE — Wave AN lock (**DONE** — PROMOTE)

> Lab: `.local/pesquisa.md` §3 AN8 · Public note: [an-freeze.md](an-freeze.md)  
> After: [wave-an-summary.md](wave-an-summary.md) / [paper-lab-wave-an.md](paper-lab-wave-an.md)

## Hypothesis

After AN-REPORT, freeze Wave AN the same way AM-FREEZE locked AM: **outcomes stay** (edge dual-arm PROMOTEs + GENEDGE HOLD); **no Wave AO** without an explicit reopen agenda.

## Gate

| Check | Result |
|-------|--------|
| AN formals keep GENEDGE HOLD · CTXEDGE…APPEDGE · HITL · REPORT decisions | **ok** |
| `wave-an-summary` · `paper-lab-wave-an` · `an-freeze` contain **COMPLETE** | **ok** |
| RECIPES + champion-card contain **H-CTXEDGE** · **AN-HITL-10** · **COMPLETE** | **ok** |
| Dual-arm LOOKUP+GENERATE smoke (`wall_ms>0`) | **ok** |
| Decision | **PROMOTE** |

## Reproduce

```bash
npm run nano:an:freeze
```

## Finding

1. Ship claim stays scoped **AF packaged stack** (AN peak gen is grounded extractive — not open chat).  
2. AN-FREEZE does **not** invent new serve/train hyps.  
3. Further research requires a new § in `.local/pesquisa.md` (Wave AO reopen).  
4. Anti-FP law remains: LOOKUP ≠ generative IQ; GENEDGE peak ≠ open-chat IQ.  
5. ≤5M hard law remains after CAPCHECK skip.

## Artifacts

- Module: `nano_lm/src/an_freeze_ops.py` · Runner: `nano_lm/src/run_an_freeze.py`
- Summary: `results/nano-lm/wave-an/an_freeze.json`
- Contract: `nano_lm/tests/test_an_freeze.py`
