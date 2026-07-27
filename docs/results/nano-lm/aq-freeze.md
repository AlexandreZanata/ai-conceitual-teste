# AQ-FREEZE — Wave AQ NO-REOPEN (**DONE** — PROMOTE)

> Lab: `.local/pesquisa.md` §5 AQ9 · After **AQ-REPORT**  
> Module: `nano_lm/src/aq_freeze_ops.py` · Runner: `npm run nano:aq:freeze`  
> Parent: [ap-freeze.md](ap-freeze.md) · [wave-aq-summary.md](wave-aq-summary.md)

## Decision

**PROMOTE** — Wave AQ outcomes locked; product pillars PROMOTE stack stays; H-NANOGEN ablated HOLD locked; ≤5M hard stays; ship claim remains **AF packaged stack + AQ product layer — not open chat LM**; **no Wave AR** without explicit lab-book reopen.

**Status: COMPLETE + FROZEN** (freeze gate).

## Locked outcomes

| ID | Decision | Must stay |
|----|----------|-----------|
| H-PARAHIT | **PROMOTE** | hit_rate 0.95 · false-hit 0 |
| H-ADVFP | **PROMOTE** | false-hit 0/20 · contrast reject |
| H-LATP | **PROMOTE** | triad p50/p99 · no FASTBASE regress |
| H-KBCOV | **PROMOTE** | 22/22 + 6 product holes |
| H-MODEUI | **PROMOTE** | LOOKUP·PEAK·DECODE visible |
| H-NANOGEN | **HOLD** | ablated gen 4.0 · peak_only_lift |
| AQ-PRODUCT-HITL | **PROMOTE** | pillars+apps; gen claim locked |
| AQ-REPORT | **PROMOTE** | [summary](wave-aq-summary.md) · [paper-lab](paper-lab-wave-aq.md) |

## Forbidden without reopen

- Invent **Wave AR** letter-pack / new H-IDs  
- Claim LOOKUP scores = generative IQ / open chat LM  
- Soft-revive QI · STREAM · GENCACHE · MIXD · GPFB-K=2 · naive CTX · ZPREF · KVCACHE-Q  
- Sell PEAK extractive as open-chat / mini-AGI unlocked  
- Sell product PROMOTE as generative unlock while H-NANOGEN HOLD  
- Raise param cap without named CAPCHECK-style reopen  

## Validate

```bash
npm run nano:aq:freeze
# optional: --skip-ask
npm run nano:aq:report
npm run nano:ap:freeze
```

Mode triad smoke must keep LOOKUP · PEAK · DECODE visible.  
Artifact: `results/nano-lm/wave-aq/aq_freeze.json` · Contract: `nano_lm/tests/test_aq_freeze.py`.
