# AO-FREEZE — Wave AO lock (**DONE** — PROMOTE)

> Lab: `.local/pesquisa.md` §3 AO8 · Public note: [ao-freeze.md](ao-freeze.md)  
> After: [wave-ao-summary.md](wave-ao-summary.md) / [paper-lab-wave-ao.md](paper-lab-wave-ao.md)

## Hypothesis

After AO-REPORT, freeze Wave AO the same way AN-FREEZE locked AN: **outcomes stay** (core dual-arm PROMOTEs + GENCORE HOLD); **no Wave AP** without an explicit reopen agenda.

## Gate

| Check | Result |
|-------|--------|
| AO formals keep GENCORE HOLD · CTXCORE…APPCORE · HITL · REPORT decisions | **ok** |
| `wave-ao-summary` · `paper-lab-wave-ao` · `ao-freeze` contain **COMPLETE** | **ok** |
| RECIPES + champion-card contain **H-CTXCORE** · **AO-HITL-10** · **COMPLETE** | **ok** |
| Dual-arm LOOKUP+GENERATE smoke (`wall_ms>0`) | **ok** |
| Decision | **PROMOTE** |

## Reproduce

```bash
npm run nano:ao:freeze
```

## Finding

1. Ship claim stays scoped **AF packaged stack** (AO peak gen is grounded extractive — not open chat).  
2. AO-FREEZE does **not** invent new serve/train hyps.  
3. Further research requires a new § in `.local/pesquisa.md` (Wave AP reopen).  
4. Anti-FP law remains: LOOKUP ≠ generative IQ; GENCORE peak ≠ open-chat IQ.  
5. ≤5M hard law remains after CAPCHECK skip.

## Artifacts

- Module: `nano_lm/src/ao_freeze_ops.py` · Runner: `nano_lm/src/run_ao_freeze.py`
- Summary: `results/nano-lm/wave-ao/ao_freeze.json`
- Contract: `nano_lm/tests/test_ao_freeze.py`
