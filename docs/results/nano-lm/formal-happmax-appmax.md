# H-APPMAX — stronger apps + route + DEPL-AE (**DONE** — PROMOTE)

> Lab: `.local/pesquisa.md` §5 AE4 · Session: `.local/wave-ae/SESSION.md`  
> Parent: **H-APPPLUS** · **H-ROUTEPLUS** · Pack: AE0 held-out asks · Spines: CTXMAX / SMARTMAX / FASTMAX  
> Module: `nano_lm/src/appmax_ops.py` · Runner: `npm run nano:appmax`

## Hypothesis

Ship **howto↑** (mean ≥ APPPLUS howto **8.3**) plus green **known/longdoc**, add optional 4th surface **`app-route`**, and DEPL-AE one-pagers — ASK→EVAL→FIX×10 per app on AE0 without open-chat claim.

## Gate (Cursor ASK→EVAL→FIX×10 / app)

| Metric | Result | Pass bar / rule |
|--------|-------:|-----------------|
| apps packaged | **4** | ≥ 4 (known + longdoc + howto + route) |
| apps PROMOTE | **4**/4 | all green · 0 KILL |
| mean across apps | **8.725** | quality ≥7 · errors ≤3 / app |
| app-known mean | **8.6** | SERVE known+howto · honest OOS |
| app-longdoc mean | **9.0** | full pack + CTXMAX ctx |
| app-howto mean | **8.3** | howto↑ ≥ APPPLUS **8.3** |
| app-route mean | **9.0** | auto-route all surfaces |
| DEPL pages ok | **5**/5 | 4 apps + [depl-ae.md](depl-ae.md) |
| false-hit | **0** | KILL if any |
| open-chat claim | **rejected** | DEPL honesty |
| Decision | **PROMOTE** | product ∧ DEPL ∧ no KILL |

## Finding

1. **app-howto** holds APPPLUS howto floor (8.3) with SMARTMAX/FASTMAX spine.  
2. **app-route** is the 4th surface — auto-selects known/howto/longdoc via `select_app`.  
3. Known/longdoc stay PROMOTE on AE0; longdoc uses CTXMAX multi-doc meta.  
4. DEPL-AE refreshes one-pagers + overview; claim remains scoped apps — **not** open chat LM.

## Reproduce

```bash
npm run nano:ae:session
npm run nano:appmax
npm run nano:appmax -- --app app-howto
npm run nano:appmax -- --app app-route
```

## Artifacts

- Summary: `results/nano-lm/wave-ae/appmax_summary.json`  
- One-pagers: [app-known.md](app-known.md) · [app-howto.md](app-howto.md) · [app-longdoc.md](app-longdoc.md) · [app-route.md](app-route.md) · [depl-ae.md](depl-ae.md)  
- Trials: `AE-APPMAX-{KNOWN,LONGDOC,HOWTO,ROUTE}-HITL-01…10`  
- Contract: `nano_lm/tests/test_appmax.py`

Next: **AE5 AE-HITL-10** (**DONE** — see [wave-ae-hitl.md](wave-ae-hitl.md)). Next wave stage: **AE6 AE-REPORT**.
