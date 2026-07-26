# Wave AE — more ctx · smarter · faster · real apps (**COMPLETE**)

> Lab: `.local/pesquisa.md` §5 · Paper-lab: [paper-lab-wave-ae.md](paper-lab-wave-ae.md)  
> Parent: Wave AD **AD-FREEZE** reopen · Product spine: **AE packaged stack**

**Status: RESEARCH COMPLETE** · Freeze pending (AE7) · Thesis: **Scoped AE packaged stack = CTXMAX+SMARTMAX+FASTMAX+APPMAX on held-out AE0; final HITL mean 9.0; not open chat LM.**

## Stage scoreboard (Cursor ASK→EVAL→FIX)

| # | ID | Mean | Errors | FIX count | Decision | Note |
|---|-----|-----:|-------:|----------:|----------|------|
| AE0 | **SESSION** | — | — | **0** | **PROMOTE** | freeze 10 held-out asks ≠ AB ≠ AC ≠ AD |
| AE1 | **H-CTXMAX** | 9 | 0 | **0** | **PROMOTE** | multi-doc L_eff↑ vs CTXPLUS |
| AE2 | **H-SMARTMAX** | 9 | 0 | **0** | **PROMOTE** | multi-hop cite; false-hit 0 |
| AE3 | **H-FASTMAX** | 9 | 0 | **0** | **PROMOTE** | hot e2e ≪ FASTPLUS warm |
| AE4 | **H-APPMAX** | 8.725 | 0 | **0** | **PROMOTE** | howto↑ + app-route + DEPL-AE |
| AE5 | **AE-HITL-10** | 9 | 0 | **0** | **PROMOTE** | final pack gate |
| AE6 | **AE-REPORT** | — | — | **0** | **PROMOTE** | public summary + paper-lab |
| AE7 | **AE-FREEZE** | — | — | **0** | **pending** | lock; no Wave AF invent |

## Honest product claims

| Claim | Truth |
|-------|-------|
| Longer usable ctx | **H-CTXMAX**; mean **9.0**; L_eff↑ vs CTXPLUS |
| Smarter retrieve/cite | **H-SMARTMAX**; mean **9.0**; false-hit **0** |
| Faster ask/TTFT | **H-FASTMAX**; hot e2e ≪ FASTPLUS warm |
| Stronger apps + route | **H-APPMAX**; 4/4 apps; mean **8.725** |
| Final HITL | **AE-HITL-10** mean **9.0** · errors **0**/10 |
| “Open chat LM ≤5M” | **False** — not open chat |

## Reproduce

```bash
npm run nano:ae:report
npm run nano:ae:session
npm run nano:ctxmax
npm run nano:smartmax
npm run nano:fastmax
npm run nano:appmax
npm run nano:ae:hitl
npm run nano:ae:freeze
```

## Do not reopen

QI · STREAM · KVCACHE-Q · GENCACHE · MIXD · GPFB-K=2 · naive CTX · ZPREF · invent Wave AF without lab-book reopen · claim open chat.
