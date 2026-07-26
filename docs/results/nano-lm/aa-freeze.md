# AA-FREEZE — Wave AA NO-REOPEN (**DONE** — PROMOTE)

> Lab: `.local/pesquisa.md` §8.2 · After **AA-REPORT**  
> Module: `nano_lm/src/aa_freeze_ops.py` · Runner: `npm run nano:aa:freeze`  
> Parent KILL freeze: [lab-freeze.md](lab-freeze.md) · Closeout: [wave-aa-summary.md](wave-aa-summary.md)

## Decision

**PROMOTE** — Wave AA outcomes locked; known-ask product remains **H-ZWRAP + H-WRAPBANK**; HOLD/KILL decisions stay; **no Wave AB** without explicit lab-book reopen.

**Status: COMPLETE** (freeze gate).

## Locked outcomes

| ID | Decision | Must stay |
|----|----------|-----------|
| H-WRAPBANK | **PROMOTE** | bank golds + HITL wrap |
| H-PARA | **HOLD** | exact-match brittleness documented |
| H-SERVEALIGN | **HOLD** | not shippable open chat |
| H-ZPREF | **KILL** | preference story regress |
| H-DEPL-DOC | **PROMOTE** | one-pagers ↔ DEPL-Y |
| AA-REPORT | **PROMOTE** | [summary](wave-aa-summary.md) · [paper-lab](paper-lab-wave-aa.md) |

## Forbidden without reopen

- Invent **Wave AB** letter-pack / new H-IDs  
- Claim SERVEALIGN / ZPREF / ZERR = interactive chat LM  
- Soft-revive QI · STREAM · GENCACHE · MIXD · GPFB-K=2 · naive CTX  
- Rewrite PARA HOLD into silent “solved” without new evidence  

## Validate

```bash
npm run nano:aa:freeze
# optional: --skip-ask
npm run nano:lab-freeze
npm run nano:aa:report
```

Wrap smoke must keep `WRAP_LOOKUP` on known-ask.  
Artifact: `results/nano-lm/wave-aa/aa_freeze.json` · Contract: `nano_lm/tests/test_aa_freeze.py`.
