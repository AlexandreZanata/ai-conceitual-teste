# AM-FREEZE — Wave AM lock (**DONE** — PROMOTE)

> Lab: `.local/pesquisa.md` §3 AM8 · Public note: [am-freeze.md](am-freeze.md)  
> After: [wave-am-summary.md](wave-am-summary.md) / [paper-lab-wave-am.md](paper-lab-wave-am.md)

## Hypothesis

After AM-REPORT, freeze Wave AM the same way AL-FREEZE locked AL: **outcomes stay** (next dual-arm PROMOTEs + GENTRUTH HOLD); **no Wave AN** without an explicit reopen agenda.

## Gate

| Check | Result |
|-------|--------|
| AM formals keep GENTRUTH HOLD · CTXNEXT…APPNEXT · HITL · REPORT decisions | **ok** |
| `wave-am-summary` · `paper-lab-wave-am` · `am-freeze` contain **COMPLETE** | **ok** |
| RECIPES + champion-card contain **H-CTXNEXT** · **AM-HITL-10** · **COMPLETE** | **ok** |
| Dual-arm LOOKUP+GENERATE smoke (`wall_ms>0`) | **ok** |
| Decision | **PROMOTE** |

## Reproduce

```bash
npm run nano:am:freeze
```

## Finding

1. Ship claim stays scoped **AF packaged stack** (AM peak gen is grounded extractive — not open chat).  
2. AM-FREEZE does **not** invent new serve/train hyps.  
3. Further research requires a new § in `.local/pesquisa.md` (Wave AN reopen).  
4. Anti-FP law remains: LOOKUP ≠ generative IQ; GENTRUTH peak ≠ open-chat IQ.  
5. ≤5M hard law remains after CAPCHECK skip.

## Artifacts

- Module: `nano_lm/src/am_freeze_ops.py` · Runner: `nano_lm/src/run_am_freeze.py`
- Summary: `results/nano-lm/wave-am/am_freeze.json`
- Contract: `nano_lm/tests/test_am_freeze.py`
