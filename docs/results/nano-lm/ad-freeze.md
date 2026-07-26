# AD-FREEZE — Wave AD NO-REOPEN (**DONE** — PROMOTE)

> Lab: `.local/pesquisa.md` §8.6 AD7 · After **AD-REPORT**  
> Module: `nano_lm/src/ad_freeze_ops.py` · Runner: `npm run nano:ad:freeze`  
> Parent: [ac-freeze.md](ac-freeze.md) · [ab-freeze.md](ab-freeze.md) · [wave-ad-summary.md](wave-ad-summary.md)

## Decision

**PROMOTE** — Wave AD outcomes locked; scoped product remains **AC/APPPLUS + AD stack** (HARDPARA · COMPOSE · ROUTEPLUS · DEPLPLUS); **no Wave AE** without explicit lab-book reopen.

**Status: COMPLETE** (freeze gate).

## Locked outcomes

| ID | Decision | Must stay |
|----|----------|-----------|
| H-HARDPARA | **PROMOTE** | adversarial para; false-hit 0 |
| H-COMPOSE | **PROMOTE** | multi-source usable 10/10 |
| H-ROUTEPLUS | **PROMOTE** | correct route + honest OOS |
| H-DEPLPLUS | **PROMOTE** | DEPL one-pagers + smoke |
| AD-HITL-10 | **PROMOTE** | final mean 9.0 |
| AD-REPORT | **PROMOTE** | [summary](wave-ad-summary.md) · [paper-lab](paper-lab-wave-ad.md) |

## Forbidden without reopen

- Invent **Wave AE** letter-pack / new H-IDs  
- Claim AD/AC stack / SERVEALIGN / ZERR = unbounded open chat LM  
- Soft-revive QI · STREAM · GENCACHE · MIXD · GPFB-K=2 · naive CTX · ZPREF  
- Rewrite held-out HITL into silent “open chat solved”  

## Validate

```bash
npm run nano:ad:freeze
# optional: --skip-ask
npm run nano:ad:report
npm run nano:ac:freeze
```

ASKFAST/SEMWRAP smoke must keep a scoped hit on held-out known-ask.  
Artifact: `results/nano-lm/wave-ad/ad_freeze.json` · Contract: `nano_lm/tests/test_ad_freeze.py`.
