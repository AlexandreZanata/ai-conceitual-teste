# AM-FREEZE — Wave AM NO-REOPEN (**DONE** — PROMOTE)

> Lab: `.local/pesquisa.md` §3 AM8 · After **AM-REPORT**  
> Module: `nano_lm/src/am_freeze_ops.py` · Runner: `npm run nano:am:freeze`  
> Parent: [al-freeze.md](al-freeze.md) · [wave-am-summary.md](wave-am-summary.md)

## Decision

**PROMOTE** — Wave AM outcomes locked; next dual-arm PROMOTE stack stays; GENTRUTH ablated HOLD locked; gen≥5 via grounded extractive peak (not open chat); ≤5M hard stays; ship claim remains **AF packaged stack**; **no Wave AN** without explicit lab-book reopen.

**Status: COMPLETE + FROZEN** (freeze gate).

## Locked outcomes

| ID | Decision | Must stay |
|----|----------|-----------|
| H-GENTRUTH | **HOLD** | ablated gen 4.0; peak_only_lift |
| H-CAPCHECK | **SKIPPED** | keep ≤5M without size reopen |
| H-CTXNEXT | **PROMOTE** | deca-doc L_eff 213147 |
| H-SMARTNEXT | **PROMOTE** | deca-hop cite; gen 9.0 |
| H-FASTNEXT | **PROMOTE** | cue-jump peak-fast hot 0.17 |
| H-APPNEXT | **PROMOTE** | dual-arm apps + DEPL-AM |
| AM-HITL-10 | **PROMOTE** | final L=9.0 G=9.0; ship=AF |
| AM-REPORT | **PROMOTE** | [summary](wave-am-summary.md) · [paper-lab](paper-lab-wave-am.md) |

## Forbidden without reopen

- Invent **Wave AN** letter-pack / new H-IDs  
- Claim LOOKUP scores = generative IQ / open chat LM  
- Soft-revive QI · STREAM · GENCACHE · MIXD · GPFB-K=2 · naive CTX · ZPREF · KVCACHE-Q  
- Sell CTXNEXT periods / LOOKUP hits as smarter open chat  
- Sell GENTRUTH extractive peak as open-chat IQ  
- Raise param cap without named CAPCHECK-style reopen  

## Validate

```bash
npm run nano:am:freeze
# optional: --skip-ask
npm run nano:am:report
npm run nano:al:freeze
```

Dual-arm smoke must keep LOOKUP + GENERATE (`wall_ms>0`) on AM0 known-ask.  
Artifact: `results/nano-lm/wave-am/am_freeze.json` · Contract: `nano_lm/tests/test_am_freeze.py`.
