# H-APPREAL — apps expose LOOKUP vs GENERATE (**DONE** — HOLD)

> Lab: `.local/pesquisa.md` §5 AG5 · Session: `.local/wave-ag/SESSION.md`  
> Parent: **H-APPULTRA** · **H-ANTIFP** · Pack: AG0 held-out asks  
> Module: `nano_lm/src/appreal_ops.py` · Runner: `npm run nano:appreal` (`nano:ag:appreal`)

## Hypothesis

Package **3 AG0 surfaces** (known-ask · howto · long-doc) that **expose dual-arm** LOOKUP vs GENERATE with DEPL-AG honesty — ASK→EVAL→FIX×10 per surface; gen mean ≥ **5.0** **or** honest **HOLD**; never claim LOOKUP as generative IQ.

## Gate (Cursor ASK→EVAL→FIX×10 dual-arm / surface)

| Metric | Result | Pass bar / rule |
|--------|-------:|-----------------|
| apps packaged | **3** | ≥ 3 (known + howto + longdoc) |
| dual-arm expose | **3**/3 | LOOKUP + GENERATE labeled |
| LOOKUP mean across | **8.33** | ≥ **7.0** |
| GENERATE mean (SERVE) | **1.0** | ≥ **5.0** for PROMOTE else **HOLD** |
| DEPL pages ok | **4**/4 | 3 apps + [depl-ag.md](depl-ag.md) |
| FALSE_HIT | **0** | any → **KILL** |
| open-chat claim | **rejected** | DEPL honesty |
| Decision | **HOLD** | expose+lookup+DEPL ok; gen &lt; 5 (honest) |

## Frontier EVAL — per app

| App | Lookup mean | Gen mean (SERVE) | Dual-arm | Decision |
|-----|------------:|-----------------:|:--------:|----------|
| app-known | ~8.7 | **1.0** | yes | **HOLD** |
| app-howto | ~8.5 | **1.0** | yes | **HOLD** |
| app-longdoc | ~8.4 | **1.0** | yes | **HOLD** |

LOOKUP = WRAP_LOOKUP TRUE_HIT / honest OOS refuse. GENERATE = QT+EARLY wrap=False period collapse on SERVE · wall_ms&gt;0.

## Finding

1. All three surfaces expose **LOOKUP vs GENERATE** with DEPL-AG dual-arm law documented.  
2. Lookup quality holds (mean **8.33**, false-hit **0**) — product retrieve path only.  
3. Generative SERVE mean stays **1.0** (periods) — below gen≥5 → **HOLD** per §5 AG5.  
4. Ship claim remains **AF packaged stack** until AG6.

## Reproduce

```bash
npm run nano:ag:session
npm run nano:appreal
# alias: npm run nano:ag:appreal
npm run nano:appreal -- --app app-howto
npm run nano:test && npm run verify
```

## Artifacts

- Summary: `results/nano-lm/wave-ag/appreal_summary.json`  
- One-pagers: [appreal-known.md](appreal-known.md) · [appreal-howto.md](appreal-howto.md) · [appreal-longdoc.md](appreal-longdoc.md) · [depl-ag.md](depl-ag.md)  
- Trials: `AG-APPREAL-{KNOWN,HOWTO,LONGDOC}-{LOOKUP\|GEN}-HITL-01…10`  
- Contract: `nano_lm/tests/test_appreal.py`

Next: **AG6 AG-HITL-10**.
