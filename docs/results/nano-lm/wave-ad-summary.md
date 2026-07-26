# Wave AD — robust held-out · hard para · compose · route · deploy (**COMPLETE**)

> Lab: `.local/pesquisa.md` §8.6 · §13 · Paper-lab: [paper-lab-wave-ad.md](paper-lab-wave-ad.md)  
> Parent: Wave AC **AC-FREEZE** reopen · Product spine: **AC/APPPLUS + AD stack**

**Status: COMPLETE** · Thesis: **Scoped AD packaged stack = HARDPARA+COMPOSE+ROUTEPLUS+DEPLPLUS on AC/APPPLUS spine; held-out HITL mean 9.0; not open chat LM.**

## Stage scoreboard (Cursor ASK→EVAL→FIX)

| # | ID | Mean | Errors | FIX count | Decision | Note |
|---|-----|-----:|-------:|----------:|----------|------|
| AD0 | **SESSION** | — | — | **0** | **PROMOTE** | freeze 10 held-out asks ≠ AB ≠ AC |
| AD1 | **H-HARDPARA** | 9 | 0 | **0** | **PROMOTE** | adversarial para; false-hit 0 |
| AD2 | **H-COMPOSE** | 9 | 0 | **0** | **PROMOTE** | usable 10/10; sources 2.0 |
| AD3 | **H-ROUTEPLUS** | 9 | 0 | **0** | **PROMOTE** | route 10/10; OOS 10/10 |
| AD4 | **H-DEPLPLUS** | 9 | 0 | **0** | **PROMOTE** | pages 4/4; DEPL honest |
| AD5 | **AD-HITL-10** | 9 | 0 | **0** | **PROMOTE** | final pack gate |
| AD6 | **AD-REPORT** | — | — | **0** | **PROMOTE** | public summary + paper-lab |
| AD7 | **AD-FREEZE** | — | — | **0** | **PROMOTE** | lock; no Wave AE invent |

## Honest product claims

| Claim | Truth |
|-------|-------|
| Harder para | **H-HARDPARA**; mean **9.0**; false-hit **0** |
| Multi-source compose | **H-COMPOSE**; usable **10**/10; sources **2.0** |
| Cross-app route + OOS | **H-ROUTEPLUS**; route/OOS **10**/10 |
| Deploy docs + smoke | **H-DEPLPLUS**; pages **4**/4 |
| Final HITL | **AD-HITL-10** mean **9.0** · errors **0**/10 |
| “Open chat LM ≤5M” | **False** — not open chat |

## Reproduce

```bash
npm run nano:ad:report
npm run nano:ad:session
npm run nano:hardpara
npm run nano:compose
npm run nano:routeplus
npm run nano:deplplus
npm run nano:ad:hitl
npm run nano:ad:freeze
```

## Do not reopen

QI · STREAM · KVCACHE-Q · GENCACHE · MIXD · GPFB-K=2 · naive CTX · ZPREF · ZERR/SERVEALIGN/AB/AC-as-open-chat · invent Wave AE without lab-book reopen.
