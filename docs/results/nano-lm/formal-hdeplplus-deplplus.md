# H-DEPLPLUS — AC+AD deploy one-pagers + smoke (**DONE** — PROMOTE)

> Lab: `.local/pesquisa.md` §8.6 AD4 · §13.1 · Session: `.local/wave-ad/SESSION.md`  
> Parent: **H-APPPLUS** · **H-ROUTEPLUS** · Pack: AD0 held-out asks  
> Module: `nano_lm/src/deplplus_ops.py` · Runner: `npm run nano:deplplus`

## Hypothesis

Ship honest DEPL one-pagers for APPPLUS apps + an AD stack overview (`depl-ad.md`), then ASK→EVAL→FIX×10 on the AD0 pack through auto-routed deploy apps — without reviving KILL serve hyps or claiming open chat.

## Gate (Cursor ASK→EVAL→FIX×10 / smoke)

| Metric | Result | Pass bar / rule |
|--------|-------:|-----------------|
| one-pagers ok | **4**/4 | ≥ 4 (3 apps + depl-ad) |
| mean score | **9.0** | ≥ 7.0 |
| errors | **0**/10 | ≤ 3 |
| FALSE_HIT | **0**/10 | any → **KILL** |
| claims honest | **yes** | required |
| FIX count | **0** | — |
| Decision | **PROMOTE** | docs ∧ smoke ∧ honesty |

## Finding

1. `app-known` / `app-howto` / `app-longdoc` + [depl-ad.md](depl-ad.md) list AD stack markers and forbidden KILLs.  
2. Smoke routes each AD0 ask via ROUTEPLUS `select_app` → SEMWRAP/ASKFAST.  
3. Claim remains scoped packaged deploy — **not** open chat LM.  
4. Forbidden unused: STREAM · KVCACHE-Q · GENCACHE · ZPREF · QI · MIXD.

## Reproduce

```bash
npm run nano:ad:session
npm run nano:deplplus
```

## Artifacts

- Summary: `results/nano-lm/wave-ad/deplplus_summary.json`  
- One-pagers: [app-known.md](app-known.md) · [app-howto.md](app-howto.md) · [app-longdoc.md](app-longdoc.md) · [depl-ad.md](depl-ad.md)  
- Trials: `results/nano-lm/wave-ad/trials/AD-DEPLPLUS-HITL-01.json` … `10.json`  
- Contract: `nano_lm/tests/test_deplplus.py`

Next: **AD5 AD-HITL-10**.
