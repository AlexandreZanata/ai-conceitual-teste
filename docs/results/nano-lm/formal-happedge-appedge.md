# H-APPEDGE — apps expose LOOKUP vs GENERATE (**DONE** — PROMOTE)

> Lab: `.local/pesquisa.md` §3 AN5 · Session: `.local/wave-an/SESSION.md`  
> Parent: **H-FASTEDGE** · **H-SMARTEDGE** · Pack: AN0 held-out asks  
> Module: `nano_lm/src/appedge_ops.py` · Runner: `npm run nano:appedge` (`nano:an:appedge`)

## Hypothesis

Package **3 AN0 surfaces** (known-ask · howto · long-doc) that **expose dual-arm** LOOKUP vs GENERATE with DEPL-AN honesty — ASK→EVAL→FIX×10 per surface; **GENEDGE** grounded+extractive SERVE beyond APPPUSH mid-open; gen mean ≥ **5.0** **or** honest **HOLD**; never claim LOOKUP as generative IQ / peak as open-chat.

## Gate (Cursor ASK→EVAL→FIX×10 dual-arm / surface)

| Metric | Result | Pass bar / rule |
|--------|-------:|-----------------|
| apps packaged | **3** | ≥ 3 (known + howto + longdoc) |
| dual-arm expose | **3**/3 | LOOKUP + GENERATE labeled |
| LOOKUP mean across | **8.33** | ≥ **7.0** |
| GENERATE mean (SERVE) | **9.0** | ≥ **5.0** for PROMOTE else **HOLD** |
| vs APPPUSH SERVE gen 4.0 | **beat** (+5.0) | peak exact vs mid-open |
| peer APPNEXT SERVE gen 9.0 | **match** | AN-aware peak |
| DEPL pages ok | **4**/4 | 3 apps + [depl-an.md](depl-an.md) |
| FALSE_HIT | **0** | any → **KILL** |
| open-chat claim | **rejected** | DEPL honesty |
| Decision | **PROMOTE** | expose+lookup+gen≥5+DEPL |

## Frontier EVAL — per app

| App | Lookup mean | Gen mean (SERVE) | Dual-arm | Decision |
|-----|------------:|-----------------:|:--------:|----------|
| app-known | **8.3** | **9.0** | yes | **PROMOTE** |
| app-howto | **8.5** | **9.0** | yes | **PROMOTE** |
| app-longdoc | **8.2** | **9.0** | yes | **PROMOTE** |

LOOKUP = WRAP_LOOKUP TRUE_HIT / honest OOS refuse. GENERATE = QPFB2+GROUNDED+GENEDGE_PEAK shared once · wall_ms>0 · peak spans (labeled ≠ open-chat IQ).

### Cursor EVAL bullets

1. In-scope SERVE gens are GENEDGE extractive peak exact golds (e.g. `18`, `a.remove(x)`, `range`) — not period collapse.  
2. OOS routes refuse honestly (not open chat).  
3. Dual-arm labels + DEPL-AN sync hold; SERVE gen **9.0** beats APPPUSH **4.0** → full PROMOTE.

## Finding

1. All three surfaces expose **LOOKUP vs GENERATE** with DEPL-AN dual-arm law documented.  
2. Lookup quality holds (mean **8.33**, false-hit **0**) — product retrieve path only.  
3. Generative SERVE mean **9.0** clears gen≥5 and peers APPNEXT via GENEDGE peak stops.  
4. Ship claim remains **AF packaged stack** until AN6.

## Reproduce

```bash
npm run nano:an:session
npm run nano:appedge
# alias: npm run nano:an:appedge
npm run nano:appedge -- --app app-howto
npm run nano:test && npm run verify
```

## Artifacts

- Summary: `results/nano-lm/wave-an/appedge_summary.json`  
- One-pagers: [appedge-known.md](appedge-known.md) · [appedge-howto.md](appedge-howto.md) · [appedge-longdoc.md](appedge-longdoc.md) · [depl-an.md](depl-an.md)  
- Trials: `AN-APPEDGE-{KNOWN,HOWTO,LONGDOC}-{LOOKUP|GEN}-HITL-01…10`  
- Contract: `nano_lm/tests/test_appedge.py`

Next: **AN6 AN-HITL-10** — final dual-arm on same 10.
