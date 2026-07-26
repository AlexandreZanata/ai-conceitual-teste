# H-APPLIFT — apps expose LOOKUP vs GENERATE (**DONE** — HOLD)

> Lab: `.local/pesquisa.md` §5 AH5 · Session: `.local/wave-ah/SESSION.md`  
> Parent: **H-APPREAL** · **H-FASTLIFT** · Pack: AH0 held-out asks  
> Module: `nano_lm/src/applift_ops.py` · Runner: `npm run nano:applift` (`nano:ah:applift`)

## Hypothesis

Package **3 AH0 surfaces** (known-ask · howto · long-doc) that **expose dual-arm** LOOKUP vs GENERATE with DEPL-AH honesty — ASK→EVAL→FIX×10 per surface; gen mean ≥ **5.0** **or** honest **HOLD**; never claim LOOKUP as generative IQ.

## Gate (Cursor ASK→EVAL→FIX×10 dual-arm / surface)

| Metric | Result | Pass bar / rule |
|--------|-------:|-----------------|
| apps packaged | **3** | ≥ 3 (known + howto + longdoc) |
| dual-arm expose | **3**/3 | LOOKUP + GENERATE labeled |
| LOOKUP mean across | **8.33** | ≥ **7.0** |
| GENERATE mean (SERVE) | **1.0** | ≥ **5.0** for PROMOTE else **HOLD** |
| DEPL pages ok | **4**/4 | 3 apps + [depl-ah.md](depl-ah.md) |
| FALSE_HIT | **0** | any → **KILL** |
| open-chat claim | **rejected** | DEPL honesty |
| Decision | **HOLD** | expose+lookup+DEPL ok; gen &lt; 5 (honest) |

## Frontier EVAL — per app

| App | Lookup mean | Gen mean (SERVE) | Dual-arm | Decision |
|-----|------------:|-----------------:|:--------:|----------|
| app-known | **8.3** | **1.0** | yes | **HOLD** |
| app-howto | **8.5** | **1.0** | yes | **HOLD** |
| app-longdoc | **8.2** | **1.0** | yes | **HOLD** |

LOOKUP = WRAP_LOOKUP TRUE_HIT / honest OOS refuse. GENERATE = QT+EARLY wrap=False period collapse on SERVE · wall_ms&gt;0.

### Cursor EVAL bullets

1. In-scope SERVE gens are `........` period collapses — not curated golds.  
2. OOS routes refuse honestly (not open chat).  
3. Dual-arm labels + DEPL-AH sync hold — PROMOTE blocked only by gen&lt;5.

## Finding

1. All three surfaces expose **LOOKUP vs GENERATE** with DEPL-AH dual-arm law documented.  
2. Lookup quality holds (mean **8.33**, false-hit **0**) — product retrieve path only.  
3. Generative SERVE mean stays **1.0** (periods) — below gen≥5 → **HOLD** per §5 AH5.  
4. Ship claim remains **AF packaged stack** until AH6.

## Reproduce

```bash
npm run nano:ah:session
npm run nano:applift
# alias: npm run nano:ah:applift
npm run nano:applift -- --app app-howto
npm run nano:test && npm run verify
```

## Artifacts

- Summary: `results/nano-lm/wave-ah/applift_summary.json`  
- One-pagers: [applift-known.md](applift-known.md) · [applift-howto.md](applift-howto.md) · [applift-longdoc.md](applift-longdoc.md) · [depl-ah.md](depl-ah.md)  
- Trials: `AH-APPLIFT-{KNOWN,HOWTO,LONGDOC}-{LOOKUP\|GEN}-HITL-01…10`  
- Contract: `nano_lm/tests/test_applift.py`

Next: **AH6 AH-HITL-10**.
