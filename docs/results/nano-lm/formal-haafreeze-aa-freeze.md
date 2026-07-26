# AA-FREEZE — Wave AA lock (**DONE** — PROMOTE)

> Lab: `.local/pesquisa.md` §8.2 · Public note: [aa-freeze.md](aa-freeze.md)  
> After: [wave-aa-summary.md](wave-aa-summary.md) / [paper-lab-wave-aa.md](paper-lab-wave-aa.md)

## Hypothesis

After AA-REPORT, the lab can freeze Wave AA the same way §8 #6 froze Y/Z KILLs: **outcomes stay**; **no Wave AB** without an explicit reopen agenda.

## Gate

| Check | Result |
|-------|--------|
| AA formals keep WRAPBANK/DEPL-DOC **PROMOTE**; PARA/SERVEALIGN **HOLD**; ZPREF **KILL** | **ok** |
| `wave-aa-summary` · `paper-lab-wave-aa` · `aa-freeze` contain **COMPLETE** | **ok** |
| RECIPES + champion-card contain **H-ZWRAP** · **H-WRAPBANK** · **COMPLETE** | **ok** |
| Wrap smoke `WRAP_LOOKUP` | **ok** |
| Decision | **PROMOTE** |

## Reproduce

```bash
npm run nano:aa:freeze
```

## Finding

1. Product claim stays known-ask wrap+bank only.  
2. AA-FREEZE does **not** invent new serve/train hyps.  
3. Further research requires a new § in `.local/pesquisa.md`.

## Artifacts

- Module: `nano_lm/src/aa_freeze_ops.py` · Runner: `nano_lm/src/run_aa_freeze.py`
- Summary: `results/nano-lm/wave-aa/aa_freeze.json`
- Contract: `nano_lm/tests/test_aa_freeze.py`
