# AE-FREEZE — Wave AE NO-REOPEN (**DONE** — PROMOTE)

> Lab: `.local/pesquisa.md` §5 AE7 · After **AE-REPORT**  
> Module: `nano_lm/src/ae_freeze_ops.py` · Runner: `npm run nano:ae:freeze`  
> Parent: [ad-freeze.md](ad-freeze.md) · [wave-ae-summary.md](wave-ae-summary.md)

## Decision

**PROMOTE** — Wave AE outcomes locked; scoped product remains **AE packaged stack** (CTXMAX · SMARTMAX · FASTMAX · APPMAX); **no Wave AF** without explicit lab-book reopen.

**Reopen (2026-07-26):** Wave AF opened via `.local/pesquisa.md` §5 — AF0 [wave-af-session.md](wave-af-session.md) **PROMOTE**; AF1 [formal-hctxultra-ctxultra.md](formal-hctxultra-ctxultra.md) **PROMOTE**; AF2 [formal-hsmartultra-smartultra.md](formal-hsmartultra-smartultra.md) **PROMOTE**; AF3 [formal-hfastultra-fastultra.md](formal-hfastultra-fastultra.md) **PROMOTE**; AF4 [formal-happultra-appultra.md](formal-happultra-appultra.md) **PROMOTE**; AF5 [wave-af-hitl.md](wave-af-hitl.md) **PROMOTE**; next **AF-REPORT**. AE freeze outcomes stay locked.

**Status: COMPLETE** (freeze gate).

## Locked outcomes

| ID | Decision | Must stay |
|----|----------|-----------|
| H-CTXMAX | **PROMOTE** | multi-doc L_eff↑ vs CTXPLUS |
| H-SMARTMAX | **PROMOTE** | multi-hop cite; false-hit 0 |
| H-FASTMAX | **PROMOTE** | hot e2e ≪ FASTPLUS warm |
| H-APPMAX | **PROMOTE** | howto↑ + app-route + DEPL-AE |
| AE-HITL-10 | **PROMOTE** | final mean 9.0 |
| AE-REPORT | **PROMOTE** | [summary](wave-ae-summary.md) · [paper-lab](paper-lab-wave-ae.md) |

## Forbidden without reopen

- Invent **Wave AF** letter-pack / new H-IDs  
- Claim AE/AD stack / SERVEALIGN / ZERR = unbounded open chat LM  
- Soft-revive QI · STREAM · GENCACHE · MIXD · GPFB-K=2 · naive CTX · ZPREF  
- Rewrite held-out HITL into silent “open chat solved”  

## Validate

```bash
npm run nano:ae:freeze
# optional: --skip-ask
npm run nano:ae:report
npm run nano:ad:freeze
```

ASKFAST/SEMWRAP smoke must keep a scoped hit on held-out known-ask.  
Artifact: `results/nano-lm/wave-ae/ae_freeze.json` · Contract: `nano_lm/tests/test_ae_freeze.py`.
