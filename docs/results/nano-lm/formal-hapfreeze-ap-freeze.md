# AP-FREEZE — Wave AP lock (**DONE** — PROMOTE)

> Lab: `.local/pesquisa.md` §3 AP8 · Public note: [ap-freeze.md](ap-freeze.md)  
> After: [wave-ap-summary.md](wave-ap-summary.md) / [paper-lab-wave-ap.md](paper-lab-wave-ap.md)

## Hypothesis

After AP-REPORT, freeze Wave AP the same way AO-FREEZE locked AO: **outcomes stay** (base dual-arm PROMOTEs + GENBASE HOLD); **no Wave AQ** without an explicit reopen agenda.

## Gate

| Check | Result |
|-------|--------|
| AP formals keep GENBASE HOLD · CTXBASE…APPBASE · HITL · REPORT decisions | **ok** |
| `wave-ap-summary` · `paper-lab-wave-ap` · `ap-freeze` contain **COMPLETE** | **ok** |
| RECIPES + champion-card contain **H-CTXBASE** · **AP-HITL-10** · **COMPLETE** | **ok** |
| Dual-arm LOOKUP+GENERATE smoke (`wall_ms>0`) | **ok** |
| Decision | **PROMOTE** |

## Reproduce

```bash
npm run nano:ap:freeze
```

## Finding

1. Ship claim stays scoped **AF packaged stack** (AP peak gen is grounded extractive — not open chat).  
2. AP-FREEZE does **not** invent new serve/train hyps.  
3. Further research requires a new § in `.local/pesquisa.md` (Wave AQ reopen).  
4. Anti-FP law remains: LOOKUP ≠ generative IQ; GENBASE peak ≠ open-chat IQ.  
5. ≤5M hard law remains after CAPCHECK skip.

## Artifacts

- Module: `nano_lm/src/ap_freeze_ops.py` · Runner: `nano_lm/src/run_ap_freeze.py`
- Summary: `results/nano-lm/wave-ap/ap_freeze.json`
- Contract: `nano_lm/tests/test_ap_freeze.py`
