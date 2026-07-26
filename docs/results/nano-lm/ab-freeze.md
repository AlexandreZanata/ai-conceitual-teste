# AB-FREEZE — Wave AB NO-REOPEN (**DONE** — PROMOTE)

> Lab: `.local/pesquisa.md` §8.4 · After **AB-REPORT**  
> Module: `nano_lm/src/ab_freeze_ops.py` · Runner: `npm run nano:ab:freeze`  
> Parent: [lab-freeze.md](lab-freeze.md) · [aa-freeze.md](aa-freeze.md) · [wave-ab-summary.md](wave-ab-summary.md)

## Decision

**PROMOTE** — Wave AB outcomes locked; scoped product remains **H-ZWRAP + H-WRAPBANK + AB stack** (SEMWRAP · ASKFAST · LONGAPP · ASKSMART · REALAPP); **no Wave AC** without explicit lab-book reopen.

**Status: COMPLETE** (freeze gate).

## Locked outcomes

| ID | Decision | Must stay |
|----|----------|-----------|
| H-SEMWRAP | **PROMOTE** | fuzzy near-known ask |
| H-ASKFAST | **PROMOTE** | fast ask path |
| H-LONGAPP | **PROMOTE** | curated L_eff≫W |
| H-ASKSMART | **PROMOTE** | constrained decode > SERVEALIGN |
| H-REALAPP | **PROMOTE** | app-known + app-longdoc |
| AB-HITL-10 | **PROMOTE** | final mean 9.0 |
| AB-REPORT | **PROMOTE** | [summary](wave-ab-summary.md) · [paper-lab](paper-lab-wave-ab.md) |

## Forbidden without reopen

- Invent **Wave AC** letter-pack / new H-IDs  
- Claim AB stack / SERVEALIGN / ZERR = unbounded open chat LM  
- Soft-revive QI · STREAM · GENCACHE · MIXD · GPFB-K=2 · naive CTX · ZPREF  
- Rewrite PARA HOLD / SERVEALIGN HOLD into silent “solved”  

## Validate

```bash
npm run nano:ab:freeze
# optional: --skip-ask
npm run nano:ab:report
npm run nano:lab-freeze
```

ASKFAST/SEMWRAP smoke must keep a scoped hit on known-ask.  
Artifact: `results/nano-lm/wave-ab/ab_freeze.json` · Contract: `nano_lm/tests/test_ab_freeze.py`.
