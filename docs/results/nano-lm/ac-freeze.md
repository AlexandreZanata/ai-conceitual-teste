# AC-FREEZE — Wave AC NO-REOPEN (**DONE** — PROMOTE)

> Lab: `.local/pesquisa.md` §8.5 AC7 · After **AC-REPORT**  
> Module: `nano_lm/src/ac_freeze_ops.py` · Runner: `npm run nano:ac:freeze`  
> Parent: [ab-freeze.md](ab-freeze.md) · [aa-freeze.md](aa-freeze.md) · [wave-ac-summary.md](wave-ac-summary.md)

## Decision

**PROMOTE** — Wave AC outcomes locked; scoped product remains **H-ZWRAP + H-WRAPBANK + AB stack + AC stack** (CTXPLUS · SMARTPLUS · FASTPLUS · APPPLUS / app-known · app-howto · app-longdoc); **no Wave AD** without explicit lab-book reopen.

**Status: COMPLETE** (freeze gate).

## Locked outcomes

| ID | Decision | Must stay |
|----|----------|-----------|
| H-CTXPLUS | **PROMOTE** | multi-slice L_eff≫AB |
| H-SMARTPLUS | **PROMOTE** | hard paraphrase; false-hit 0 |
| H-FASTPLUS | **PROMOTE** | held-out ask latency ↓ |
| H-APPPLUS | **PROMOTE** | app-howto + known/longdoc |
| AC-HITL-10 | **PROMOTE** | final mean 9.0 |
| AC-REPORT | **PROMOTE** | [summary](wave-ac-summary.md) · [paper-lab](paper-lab-wave-ac.md) |

## Forbidden without reopen

- Invent **Wave AD** letter-pack / new H-IDs  
- Claim AC/AB stack / SERVEALIGN / ZERR = unbounded open chat LM  
- Soft-revive QI · STREAM · GENCACHE · MIXD · GPFB-K=2 · naive CTX · ZPREF  
- Rewrite held-out HITL into silent “open chat solved”  

## Validate

```bash
npm run nano:ac:freeze
# optional: --skip-ask
npm run nano:ac:report
npm run nano:ab:freeze
```

ASKFAST/SEMWRAP smoke must keep a scoped hit on known-ask.  
Artifact: `results/nano-lm/wave-ac/ac_freeze.json` · Contract: `nano_lm/tests/test_ac_freeze.py`.
