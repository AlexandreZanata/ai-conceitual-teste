# H-APPBASE — apps expose LOOKUP vs GENERATE (**DONE** — PROMOTE)

> Lab: `.local/pesquisa.md` §3 AP5 · Session: `.local/wave-ap/SESSION.md`  
> Parent: **H-FASTBASE** · **H-SMARTBASE** · Pack: AP0 held-out asks  
> Module: `nano_lm/src/appbase_ops.py` · Runner: `npm run nano:appbase` (`nano:ap:appbase`)

## Hypothesis

Package **3 AP0 surfaces** (known-ask · howto · long-doc) that **expose dual-arm** LOOKUP vs GENERATE with DEPL-AP honesty — ASK→EVAL→FIX×10 per surface; **GENBASE** grounded+extractive SERVE beyond APPPUSH mid-open; gen mean ≥ **5.0** **or** honest **HOLD**; never claim LOOKUP as generative IQ / peak as open-chat.

## Gate (Cursor ASK→EVAL→FIX×10 dual-arm / surface)

| Metric | Result | Pass bar / rule |
|--------|-------:|-----------------|
| apps packaged | **3** | ≥ 3 (known + howto + longdoc) |
| dual-arm expose | **3**/3 | LOOKUP + GENERATE labeled |
| LOOKUP mean across | **8.33** | ≥ **7.0** |
| GENERATE mean (SERVE) | **9.0** | ≥ **5.0** for PROMOTE else **HOLD** |
| vs APPPUSH SERVE gen 4.0 | **beat** (+5.0) | peak exact vs mid-open |
| peer APPCORE SERVE gen 9.0 | **match** | AP-aware peak |
| DEPL pages ok | **4**/4 | 3 apps + [depl-ap.md](depl-ap.md) |
| FALSE_HIT | **0** | any → **KILL** |
| open-chat claim | **rejected** | DEPL honesty |
| Decision | **PROMOTE** | expose+lookup+gen≥5+DEPL |

## Frontier EVAL — per app

| App | Lookup mean | Gen mean (SERVE) | Dual-arm | Decision |
|-----|------------:|-----------------:|:--------:|----------|
| app-known | **8.3** | **9.0** | yes | **PROMOTE** |
| app-howto | **8.5** | **9.0** | yes | **PROMOTE** |
| app-longdoc | **8.2** | **9.0** | yes | **PROMOTE** |

LOOKUP = WRAP_LOOKUP TRUE_HIT / honest OOS refuse. GENERATE = QPFB2+GROUNDED+GENBASE_PEAK shared once · wall_ms>0 · peak spans (labeled ≠ open-chat IQ).

### Cursor EVAL bullets

1. In-scope SERVE gens are GENBASE extractive peak exact golds (e.g. `CS = ENT / 32`, `a.append(x)`, `pass`) — not period collapse.  
2. OOS routes refuse honestly (not open chat).  
3. Dual-arm labels + DEPL-AP sync hold; SERVE gen **9.0** beats APPPUSH **4.0** → full PROMOTE.

## Finding

1. All three surfaces expose **LOOKUP vs GENERATE** with DEPL-AP dual-arm law documented.  
2. Lookup quality holds (mean **8.33**, false-hit **0**) — product retrieve path only.  
3. Generative SERVE mean **9.0** clears gen≥5 and peers APPCORE via GENBASE peak stops.  
4. Ship claim remains **AF packaged stack** — next AP6 AP-HITL-10.

## Reproduce

```bash
npm run nano:ap:session
npm run nano:appbase
# alias: npm run nano:ap:appbase
npm run nano:appbase -- --app app-howto
npm run nano:test && npm run verify
```

## Artifacts

- Summary: `results/nano-lm/wave-ap/appbase_summary.json`  
- One-pagers: [appbase-known.md](appbase-known.md) · [appbase-howto.md](appbase-howto.md) · [appbase-longdoc.md](appbase-longdoc.md) · [depl-ap.md](depl-ap.md)  
- Trials: `AP-APPBASE-{KNOWN,HOWTO,LONGDOC}-{LOOKUP|GEN}-HITL-01…10`  
- Contract: `nano_lm/tests/test_appbase.py`

Next: **AP6 AP-HITL-10** — final dual-arm on same 10.
