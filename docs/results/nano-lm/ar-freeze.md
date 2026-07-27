# AR-FREEZE — Wave AR NO-REOPEN (**DONE** — PROMOTE)

> Lab: `.local/pesquisa.md` §5 AR8 · After **AR-REPORT**  
> Module: `nano_lm/src/ar_freeze_ops.py` · Runner: `npm run nano:ar:freeze`  
> Parent: [aq-freeze.md](aq-freeze.md) · [wave-ar-summary.md](wave-ar-summary.md)

## Decision

**PROMOTE** — Wave AR outcomes locked; core product ABSTAIN·SHIPDEMO PROMOTE stays; deepen HOLD/KILL locked; H-NANOGEN2 ablated HOLD locked; ≤5M hard stays; ship claim remains **AF packaged stack + AQ product layer — not open chat LM**; **no Wave AS** without explicit lab-book reopen.

**Status: COMPLETE + FROZEN** (freeze gate).

## Locked outcomes

| ID | Decision | Must stay |
|----|----------|-----------|
| H-ABSTAIN | **PROMOTE** | OOD abstain 1.0 · FH 0 |
| H-SHIPDEMO | **PROMOTE** | LOOKUP·PEAK·DECODE·ABSTAIN |
| H-PARAEXT | **HOLD** | hit 0.65 < 0.70 · FH 0 |
| H-ADVREG | **KILL** | false-hit 2/20 · SAFE≠quality |
| H-NANOGEN2 | **HOLD** | ablated gen 4.3 · peak_only |
| AR-DUAL-HITL | **HOLD** | core pass · soft deepen · gen locked |
| AR-REPORT | **PROMOTE** | [summary](wave-ar-summary.md) · [paper-lab](paper-lab-wave-ar.md) |

## Forbidden without reopen

- Invent **Wave AS** letter-pack / new H-IDs  
- Claim LOOKUP scores = generative IQ / open chat LM  
- Soft-revive QI · STREAM · GENCACHE · MIXD · GPFB-K=2 · naive CTX · ZPREF · KVCACHE-Q  
- Sell PEAK / bank-grounded as open-chat / mini-AGI unlocked  
- Sell SAFE mean as answer quality  
- Sell product soft HOLD as generative unlock while H-NANOGEN2 HOLD  
- Raise param cap without named CAPCHECK-style reopen  

## Validate

```bash
npm run nano:ar:freeze
# optional: --skip-ask
npm run nano:ar:report
npm run nano:aq:freeze
```

Four-mode smoke must keep LOOKUP · PEAK · DECODE · ABSTAIN visible.  
Artifact: `results/nano-lm/wave-ar/ar_freeze.json` · Contract: `nano_lm/tests/test_ar_freeze.py`.
