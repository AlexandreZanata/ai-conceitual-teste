# AO-FREEZE — Wave AO NO-REOPEN (**DONE** — PROMOTE)

> Lab: `.local/pesquisa.md` §3 AO8 · After **AO-REPORT**  
> Module: `nano_lm/src/ao_freeze_ops.py` · Runner: `npm run nano:ao:freeze`  
> Parent: [an-freeze.md](an-freeze.md) · [wave-ao-summary.md](wave-ao-summary.md)

## Decision

**PROMOTE** — Wave AO outcomes locked; core dual-arm PROMOTE stack stays; GENCORE ablated HOLD locked; gen≥5 via grounded extractive peak (not open chat); ≤5M hard stays; ship claim remains **AF packaged stack**; **no Wave AP** without explicit lab-book reopen.

**Status: COMPLETE + FROZEN** (freeze gate).

## Locked outcomes

| ID | Decision | Must stay |
|----|----------|-----------|
| H-GENCORE | **HOLD** | ablated gen 4.0; peak_only_lift |
| H-CAPCHECK | **SKIPPED** | keep ≤5M without size reopen |
| H-CTXCORE | **PROMOTE** | dodeca-doc L_eff 253105 |
| H-SMARTCORE | **PROMOTE** | dodeca-hop cite; gen 9.0 |
| H-FASTCORE | **PROMOTE** | peak-fast warm 0.06 |
| H-APPCORE | **PROMOTE** | dual-arm apps + DEPL-AO |
| AO-HITL-10 | **PROMOTE** | final L=9.0 G=9.0; ship=AF |
| AO-REPORT | **PROMOTE** | [summary](wave-ao-summary.md) · [paper-lab](paper-lab-wave-ao.md) |

## Forbidden without reopen

- Invent **Wave AP** letter-pack / new H-IDs  
- Claim LOOKUP scores = generative IQ / open chat LM  
- Soft-revive QI · STREAM · GENCACHE · MIXD · GPFB-K=2 · naive CTX · ZPREF · KVCACHE-Q  
- Sell CTXCORE periods / LOOKUP hits as smarter open chat  
- Sell GENCORE extractive peak as open-chat IQ  
- Raise param cap without named CAPCHECK-style reopen  

## Validate

```bash
npm run nano:ao:freeze
# optional: --skip-ask
npm run nano:ao:report
npm run nano:an:freeze
```

Dual-arm smoke must keep LOOKUP + GENERATE (`wall_ms>0`) on AO0 known-ask.  
Artifact: `results/nano-lm/wave-ao/ao_freeze.json` · Contract: `nano_lm/tests/test_ao_freeze.py`.
