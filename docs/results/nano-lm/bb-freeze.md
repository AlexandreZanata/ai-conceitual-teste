# BB-FREEZE — Wave BB NO-REOPEN (**DONE** — PROMOTE)

> Lab: `.local/pesquisa.md` §8 BB7 · After **BB-REPORT**  
> Module: `nano_lm/src/bb_freeze_ops.py` · Runner: `npm run nano:bb:freeze`  
> Parent: [ba-freeze.md](ba-freeze.md) · [wave-bb-summary.md](wave-bb-summary.md)

## Decision

**PROMOTE** — Wave BB outcomes locked; H-INTENTGEN·H-FASTHOLD·H-CTXHOLD PROMOTE stays; H-NANOGEN12 **DEFER** (gen stance defer · CAPCHECK closed · NANOGEN6·7 HOLD · NANOGEN8·9·10·11 DEFER cited · not NANOGEN11 rename) locked; BB-REAL-EVAL battery 12/12 PROMOTE locked; ≤5M hard stays; ship claim remains **AF packaged stack + AQ product layer + AS trust path + ablated DECODE (snippet-prefix + gibberish-tail STRICT) — not unlabeled open chat LM · not TAC unlocked**; **no Wave BC** without explicit lab-book reopen.

**Status: COMPLETE + FROZEN** (freeze gate).

## Locked outcomes

| ID | Decision | Must stay |
|----|----------|-----------|
| H-INTENTGEN | **PROMOTE** | BB-FOREVER FH 0 · BA hold 0 · AZ hold 0 · over-refuse 0 · live FP 0 · no bank stuffing |
| H-FASTHOLD | **PROMOTE** | prod p50/p99 hold · anti-FP hold · ≠ BA `nano:ba:fastreal` · ≠ AG `nano:fastreal` |
| H-CTXHOLD | **PROMOTE** | howto·cite·long content_ok · BB/BA/AZ anti-FP · L_eff alone ≠ win |
| H-NANOGEN12 | **DEFER** | stance defer · CAPCHECK closed · NANOGEN6·7 HOLD · NANOGEN8·9·10·11 DEFER cited · not NANOGEN11+rename |
| BB-REAL-EVAL | **PROMOTE** | live battery 12/12 · BB-FOREVER ABSTAIN · over-refuse LOOKUP · gen locked |
| BB-REPORT | **PROMOTE** | [summary](wave-bb-summary.md) · [paper-lab](paper-lab-wave-bb.md) |

## Forbidden without reopen

- Invent **Wave BC** letter-pack / new H-IDs  
- Claim LOOKUP scores = generative IQ / unlabeled open chat  
- BB-FOREVER intent LOOKUP sold as success  
- Over-refuse exact gold sold as safe win  
- Soft-revive QI · STREAM · GENCACHE · MIXD · GPFB-K=2 · naive CTX · ZPREF · KVCACHE-Q  
- Sell PEAK / bank-grounded / span-fallback as GPT-class / true-continue unlock  
- Sell SAFE mean as answer quality  
- Sell NANOGEN12 DEFER / NANOGEN8·9·10·11 DEFER / NANOGEN6·7 HOLD as gen unlock / mini-AGI  
- NANOGEN12 = NANOGEN11+rename / truncate-to-span as gen IQ  
- Bank stuffing BB-FOREVER  
- CTX/SMART/FAST/APP letter clones without named product hole  
- Raise param cap without named CAPCHECK-style reopen  
- Rewrite BA/AZ/AY/AX/AW/AV/AU/AT/AS/AR/AQ/AP locked outcomes  

## Validate

```bash
npm run nano:bb:freeze
# optional: --skip-ask
npm run nano:bb:report
npm run nano:ba:freeze
```

BB forever/modes smoke must keep LOOKUP · BB-FOREVER ABSTAIN · over-refuse LOOKUP · OOD ABSTAIN honest.  
Artifact: `results/nano-lm/wave-bb/bb_freeze.json` · Contract: `nano_lm/tests/test_bb_freeze.py`.
