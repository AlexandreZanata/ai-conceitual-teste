# AP-FREEZE — Wave AP NO-REOPEN (**DONE** — PROMOTE)

> Lab: `.local/pesquisa.md` §3 AP8 · After **AP-REPORT**  
> Module: `nano_lm/src/ap_freeze_ops.py` · Runner: `npm run nano:ap:freeze`  
> Parent: [ao-freeze.md](ao-freeze.md) · [wave-ap-summary.md](wave-ap-summary.md)

## Decision

**PROMOTE** — Wave AP outcomes locked; base dual-arm PROMOTE stack stays; GENBASE ablated HOLD locked; gen≥5 via grounded extractive peak (not open chat); ≤5M hard stays; ship claim remains **AF packaged stack**; **no Wave AQ** without explicit lab-book reopen.

**Status: COMPLETE + FROZEN** (freeze gate).

## Locked outcomes

| ID | Decision | Must stay |
|----|----------|-----------|
| H-GENBASE | **HOLD** | ablated gen 4.0; peak_only_lift |
| H-CAPCHECK | **SKIPPED** | keep ≤5M without size reopen |
| H-CTXBASE | **PROMOTE** | trideca-doc L_eff 274198 |
| H-SMARTBASE | **PROMOTE** | trideca-hop cite; gen 9.0 |
| H-FASTBASE | **PROMOTE** | peak-fast warm 0.056 |
| H-APPBASE | **PROMOTE** | dual-arm apps + DEPL-AP |
| AP-HITL-10 | **PROMOTE** | final L=9.0 G=9.0; ship=AF |
| AP-REPORT | **PROMOTE** | [summary](wave-ap-summary.md) · [paper-lab](paper-lab-wave-ap.md) |

## Forbidden without reopen

- Invent **Wave AQ** letter-pack / new H-IDs  
- Claim LOOKUP scores = generative IQ / open chat LM  
- Soft-revive QI · STREAM · GENCACHE · MIXD · GPFB-K=2 · naive CTX · ZPREF · KVCACHE-Q  
- Sell CTXBASE periods / LOOKUP hits as smarter open chat  
- Sell GENBASE extractive peak as open-chat IQ  
- Raise param cap without named CAPCHECK-style reopen  

## Validate

```bash
npm run nano:ap:freeze
# optional: --skip-ask
npm run nano:ap:report
npm run nano:ao:freeze
```

Dual-arm smoke must keep LOOKUP + GENERATE (`wall_ms>0`) on AP0 known-ask.  
Artifact: `results/nano-lm/wave-ap/ap_freeze.json` · Contract: `nano_lm/tests/test_ap_freeze.py`.
