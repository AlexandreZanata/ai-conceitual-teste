# AL-FREEZE — Wave AL lock (**DONE** — PROMOTE)

> Lab: `.local/pesquisa.md` §3 AL8 · Public note: [al-freeze.md](al-freeze.md)  
> After: [wave-al-summary.md](wave-al-summary.md) / [paper-lab-wave-al.md](paper-lab-wave-al.md)

## Hypothesis

After AL-REPORT, freeze Wave AL the same way AK-FREEZE locked AK: **outcomes stay** (fresh dual-arm PROMOTEs + GENFRESH HOLD); **no Wave AM** without an explicit reopen agenda.

## Gate

| Check | Result |
|-------|--------|
| AL formals keep GENFRESH HOLD · CTXFRESH…APPFRESH · HITL · REPORT decisions | **ok** |
| `wave-al-summary` · `paper-lab-wave-al` · `al-freeze` contain **COMPLETE** | **ok** |
| RECIPES + champion-card contain **H-CTXFRESH** · **AL-HITL-10** · **COMPLETE** | **ok** |
| Dual-arm LOOKUP+GENERATE smoke (`wall_ms>0`) | **ok** |
| Decision | **PROMOTE** |

## Reproduce

```bash
npm run nano:al:freeze
```

## Finding

1. Ship claim stays scoped **AF packaged stack** (AL peak gen is grounded extractive — not open chat).  
2. AL-FREEZE does **not** invent new serve/train hyps.  
3. Further research requires a new § in `.local/pesquisa.md` (Wave AM reopen).  
4. Anti-FP law remains: LOOKUP ≠ generative IQ; GENFRESH peak ≠ open-chat IQ.  
5. ≤5M hard law remains after CAPCHECK skip.

## Artifacts

- Module: `nano_lm/src/al_freeze_ops.py` · Runner: `nano_lm/src/run_al_freeze.py`
- Summary: `results/nano-lm/wave-al/al_freeze.json`
- Contract: `nano_lm/tests/test_al_freeze.py`
