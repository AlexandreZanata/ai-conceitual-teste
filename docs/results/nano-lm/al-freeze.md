# AL-FREEZE — Wave AL NO-REOPEN (**DONE** — PROMOTE)

> Lab: `.local/pesquisa.md` §3 AL8 · After **AL-REPORT**  
> Module: `nano_lm/src/al_freeze_ops.py` · Runner: `npm run nano:al:freeze`  
> Parent: [ak-freeze.md](ak-freeze.md) · [wave-al-summary.md](wave-al-summary.md)

## Decision

**PROMOTE** — Wave AL outcomes locked; fresh dual-arm PROMOTE stack stays; GENFRESH ablated HOLD locked; gen≥5 via grounded extractive peak (not open chat); ≤5M hard stays; ship claim remains **AF packaged stack**; **no Wave AM** without explicit lab-book reopen.

**Status: COMPLETE + FROZEN** (freeze gate).

## Locked outcomes

| ID | Decision | Must stay |
|----|----------|-----------|
| H-GENFRESH | **HOLD** | ablated gen 4.0; peak_only_lift |
| H-CAPCHECK | **SKIPPED** | keep ≤5M without size reopen |
| H-CTXFRESH | **PROMOTE** | nona-doc L_eff 200344 |
| H-SMARTFRESH | **PROMOTE** | nona-hop cite; gen 9.0 |
| H-FASTFRESH | **PROMOTE** | cue-first peak-fast hot ~0.2 |
| H-APPFRESH | **PROMOTE** | dual-arm apps + DEPL-AL |
| AL-HITL-10 | **PROMOTE** | final L=9.0 G=9.0; ship=AF |
| AL-REPORT | **PROMOTE** | [summary](wave-al-summary.md) · [paper-lab](paper-lab-wave-al.md) |

## Forbidden without reopen

- Invent **Wave AM** letter-pack / new H-IDs  
- Claim LOOKUP scores = generative IQ / open chat LM  
- Soft-revive QI · STREAM · GENCACHE · MIXD · GPFB-K=2 · naive CTX · ZPREF · KVCACHE-Q  
- Sell CTXFRESH periods / LOOKUP hits as smarter open chat  
- Sell GENFRESH extractive peak as open-chat IQ  
- Raise param cap without named CAPCHECK-style reopen  

## Validate

```bash
npm run nano:al:freeze
# optional: --skip-ask
npm run nano:al:report
npm run nano:ak:freeze
```

Dual-arm smoke must keep LOOKUP + GENERATE (`wall_ms>0`) on AL0 known-ask.  
Artifact: `results/nano-lm/wave-al/al_freeze.json` · Contract: `nano_lm/tests/test_al_freeze.py`.
