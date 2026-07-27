# AS-FREEZE — Wave AS NO-REOPEN (**DONE** — PROMOTE)

> Lab: `.local/pesquisa.md` §5 AS10 · After **AS-REPORT**  
> Module: `nano_lm/src/as_freeze_ops.py` · Runner: `npm run nano:as:freeze`  
> Parent: [ar-freeze.md](ar-freeze.md) · [wave-as-summary.md](wave-as-summary.md)

## Decision

**PROMOTE** — Wave AS outcomes locked; product trust ASKABSTAIN·SEMFIX·ADVSAFE·PARAEXT2·METRICS·SHIPUI PROMOTE stays; H-NANOGEN3 ablated HOLD locked; AS-DUAL-HITL product PROMOTE with gen locked; ≤5M hard stays; ship claim remains **AF packaged stack + AQ product layer — not open chat LM**; **no Wave AT** without explicit lab-book reopen.

**Status: COMPLETE + FROZEN** (freeze gate).

## Locked outcomes

| ID | Decision | Must stay |
|----|----------|-----------|
| H-ASKABSTAIN | **PROMOTE** | default-ask OOD abstain · FH 0 |
| H-SEMFIX | **PROMOTE** | ADVREG-01/05 class FH 0 |
| H-ADVSAFE | **PROMOTE** | false-hit 0/20 · SAFE≠quality |
| H-PARAEXT2 | **PROMOTE** | hit 0.80 · FH 0 |
| H-METRICS | **PROMOTE** | tetrad p50/p99 + KB holes |
| H-SHIPUI | **PROMOTE** | LOOKUP·PEAK·DECODE·ABSTAIN |
| H-NANOGEN3 | **HOLD** | ablated gen 4.3 · peak_only |
| AS-DUAL-HITL | **PROMOTE** | product pass · gen locked |
| AS-REPORT | **PROMOTE** | [summary](wave-as-summary.md) · [paper-lab](paper-lab-wave-as.md) |

## Forbidden without reopen

- Invent **Wave AT** letter-pack / new H-IDs  
- Claim LOOKUP scores = generative IQ / open chat LM  
- Soft-revive QI · STREAM · GENCACHE · MIXD · GPFB-K=2 · naive CTX · ZPREF · KVCACHE-Q  
- Sell PEAK / bank-grounded as open-chat / mini-AGI unlocked  
- Sell SAFE mean as answer quality  
- Sell product PROMOTE as generative unlock while H-NANOGEN3 HOLD  
- CTX/SMART/FAST/APP letter clones without named product hole  
- Raise param cap without named CAPCHECK-style reopen  

## Validate

```bash
npm run nano:as:freeze
# optional: --skip-ask
npm run nano:as:report
npm run nano:ar:freeze
```

Four-mode smoke must keep LOOKUP · PEAK · DECODE · ABSTAIN visible.  
Artifact: `results/nano-lm/wave-as/as_freeze.json` · Contract: `nano_lm/tests/test_as_freeze.py`.
