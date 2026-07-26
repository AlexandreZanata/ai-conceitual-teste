# H-APPULTRA — stronger apps + compose 5th + DEPL-AF (**DONE** — PROMOTE)

> Lab: `.local/pesquisa.md` §5 AF4 · Session: `.local/wave-af/SESSION.md`  
> Parent: **H-APPMAX** · Spines: CTXULTRA / SMARTULTRA / FASTULTRA · Pack: AF0 held-out asks  
> Module: `nano_lm/src/appultra_ops.py` · Runner: `npm run nano:appultra` (`nano:af:appultra`)

## Hypothesis

Ship **howto↑** (mean ≥ APPMAX howto **8.3**) and **mean↑** (≥ APPMAX mean **8.725**) across **5** packaged apps (known · longdoc · howto · route · **compose**), with DEPL-AF one-pagers — ASK→EVAL→FIX×10 per app on AF0 without open-chat claim.

## Gate (Cursor ASK→EVAL→FIX×10 / app)

| Metric | Result | Pass bar / rule |
|--------|-------:|-----------------|
| apps packaged | **5** | ≥ 5 (known + longdoc + howto + route + compose) |
| apps PROMOTE | **5**/5 | all green · 0 KILL |
| mean across apps | **8.86** | ≥ APPMAX **8.725** |
| app-known mean | **8.8** | SERVE known+howto · honest OOS |
| app-longdoc mean | **9.0** | full pack + CTXULTRA triple-doc |
| app-howto mean | **8.5** | howto↑ ≥ APPMAX **8.3** |
| app-route mean | **9.0** | auto-route all surfaces |
| app-compose mean | **9.0** | 5th surface · CTXULTRA compose |
| DEPL pages ok | **6**/6 | 5 apps + [depl-af.md](depl-af.md) |
| false-hit | **0** | KILL if any |
| open-chat claim | **rejected** | DEPL honesty |
| Decision | **PROMOTE** | product ∧ DEPL ∧ no KILL |

## Frontier EVAL (Cursor) — per-app means

| App | Mean | Errors | FIX | Notes |
|-----|-----:|-------:|----:|-------|
| app-known | **8.8** | 0 | 2 | OOS long-doc refuse honest |
| app-longdoc | **9.0** | 0 | 0 | CTXULTRA triple-doc SERVE |
| app-howto | **8.5** | 0 | 5 | OOS non-howto refuse; howto TRUE_HIT |
| app-route | **9.0** | 0 | 0 | select_app → canonical SERVE |
| app-compose | **9.0** | 0 | 0 | multi-doc compose SERVE |

Sample SERVE checks: BIP purpose · Point class · `range(3)` · Core P2P · TLS handshake — match pack gold. OOS replies name the wrong surface and redirect — score 8, not fabricated answers.

## Finding

1. **app-howto** beats APPMAX howto floor (8.5 ≥ 8.3) with SMARTULTRA/FASTULTRA spine.  
2. **app-compose** is the 5th surface — CTXULTRA triple-doc + SEMWRAP on full AF0 pack.  
3. **app-route** auto-selects known/howto/longdoc; mean across apps **8.86** > APPMAX **8.725**.  
4. DEPL-AF writes `appultra-*.md` + overview; claim remains scoped apps — **not** open chat LM.

## Reproduce

```bash
npm run nano:af:session
npm run nano:appultra
npm run nano:appultra -- --app app-howto
npm run nano:appultra -- --app app-compose
# alias: npm run nano:af:appultra
```

## Artifacts

- Summary: `results/nano-lm/wave-af/appultra_summary.json`  
- One-pagers: [appultra-known.md](appultra-known.md) · [appultra-howto.md](appultra-howto.md) · [appultra-longdoc.md](appultra-longdoc.md) · [appultra-route.md](appultra-route.md) · [appultra-compose.md](appultra-compose.md) · [depl-af.md](depl-af.md)  
- Trials: `AF-APPULTRA-{KNOWN,LONGDOC,HOWTO,ROUTE,COMPOSE}-HITL-01…10`  
- Contract: `nano_lm/tests/test_appultra.py`

Next: **AF5 AF-HITL-10** (**DONE** — see [wave-af-hitl.md](wave-af-hitl.md)). Next wave stage: **AF6 AF-REPORT**.
