# AG-FREEZE — Wave AG NO-REOPEN (**DONE** — PROMOTE)

> Lab: `.local/pesquisa.md` §5 AG8 · After **AG-REPORT**  
> Module: `nano_lm/src/ag_freeze_ops.py` · Runner: `npm run nano:ag:freeze`  
> Parent: [af-freeze.md](af-freeze.md) · [wave-ag-summary.md](wave-ag-summary.md)

## Decision

**PROMOTE** — Wave AG outcomes locked; anti-FP dual-arm discipline stays; ship claim remains **AF packaged stack**; **no Wave AH** without explicit lab-book reopen.

**Status: COMPLETE + FROZEN** (freeze gate).

## Locked outcomes

| ID | Decision | Must stay |
|----|----------|-----------|
| H-ANTIFP | **PROMOTE** | LOOKUP≠GEN harness |
| H-CTXREAL | **PROMOTE** | quad-doc L_eff↑ |
| H-SMARTREAL | **HOLD** | cite ok; gen<5 honest |
| H-FASTREAL | **PROMOTE** | gen wall↓; ≠ LOOKUP speed IQ |
| H-APPREAL | **HOLD** | dual-arm apps + DEPL-AG |
| AG-HITL-10 | **HOLD** | final L=9.0 G=1.0; ship=AF |
| AG-REPORT | **PROMOTE** | [summary](wave-ag-summary.md) · [paper-lab](paper-lab-wave-ag.md) |

## Forbidden without reopen

- Invent **Wave AH** letter-pack / new H-IDs  
- Claim LOOKUP scores = generative IQ / open chat LM  
- Soft-revive QI · STREAM · GENCACHE · MIXD · GPFB-K=2 · naive CTX · ZPREF · KVCACHE-Q  
- Rewrite dual-arm HOLD into silent “smarter LM solved”  

## Validate

```bash
npm run nano:ag:freeze
# optional: --skip-ask
npm run nano:ag:report
npm run nano:af:freeze
```

Dual-arm smoke must keep LOOKUP + GENERATE (`wall_ms>0`) on AG0 known-ask.  
Artifact: `results/nano-lm/wave-ag/ag_freeze.json` · Contract: `nano_lm/tests/test_ag_freeze.py`.
