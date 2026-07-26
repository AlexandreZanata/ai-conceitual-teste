# H-APPNEXT — apps expose LOOKUP vs GENERATE (**DONE** — PROMOTE)

> Lab: `.local/pesquisa.md` §3 AM5 · Session: `.local/wave-am/SESSION.md`  
> Parent: **H-FASTNEXT** · **H-SMARTNEXT** · Pack: AM0 held-out asks  
> Module: `nano_lm/src/appnext_ops.py` · Runner: `npm run nano:appnext` (`nano:am:appnext`)

## Hypothesis

Package **3 AM0 surfaces** (known-ask · howto · long-doc) that **expose dual-arm** LOOKUP vs GENERATE with DEPL-AM honesty — ASK→EVAL→FIX×10 per surface; **GENTRUTH** grounded+extractive SERVE beyond APPPUSH mid-open; gen mean ≥ **5.0** **or** honest **HOLD**; never claim LOOKUP as generative IQ / peak as open-chat.

## Gate (Cursor ASK→EVAL→FIX×10 dual-arm / surface)

| Metric | Result | Pass bar / rule |
|--------|-------:|-----------------|
| apps packaged | **3** | ≥ 3 (known + howto + longdoc) |
| dual-arm expose | **3**/3 | LOOKUP + GENERATE labeled |
| LOOKUP mean across | **8.33** | ≥ **7.0** |
| GENERATE mean (SERVE) | **9.0** | ≥ **5.0** for PROMOTE else **HOLD** |
| vs APPPUSH SERVE gen 4.0 | **beat** (+5.0) | peak exact vs mid-open |
| peer APPFRESH SERVE gen 9.0 | **match** | AM-aware peak |
| DEPL pages ok | **4**/4 | 3 apps + [depl-am.md](depl-am.md) |
| FALSE_HIT | **0** | any → **KILL** |
| open-chat claim | **rejected** | DEPL honesty |
| Decision | **PROMOTE** | expose+lookup+gen≥5+DEPL |

## Frontier EVAL — per app

| App | Lookup mean | Gen mean (SERVE) | Dual-arm | Decision |
|-----|------------:|-----------------:|:--------:|----------|
| app-known | **8.3** | **9.0** | yes | **PROMOTE** |
| app-howto | **8.5** | **9.0** | yes | **PROMOTE** |
| app-longdoc | **8.2** | **9.0** | yes | **PROMOTE** |

LOOKUP = WRAP_LOOKUP TRUE_HIT / honest OOS refuse. GENERATE = QPFB2+GROUNDED+GENTRUTH_PEAK shared once · wall_ms>0 · peak spans (labeled ≠ open-chat IQ).

### Cursor EVAL bullets

1. In-scope SERVE gens are GENTRUTH extractive peak exact golds (e.g. `15`, `a.index(x)`, `setattr`) — not period collapse.  
2. OOS routes refuse honestly (not open chat).  
3. Dual-arm labels + DEPL-AM sync hold; SERVE gen **9.0** beats APPPUSH **4.0** → full PROMOTE.

## Finding

1. All three surfaces expose **LOOKUP vs GENERATE** with DEPL-AM dual-arm law documented.  
2. Lookup quality holds (mean **8.33**, false-hit **0**) — product retrieve path only.  
3. Generative SERVE mean **9.0** clears gen≥5 and peers APPFRESH via GENTRUTH peak stops.  
4. Ship claim remains **AF packaged stack** until AM6.

## Reproduce

```bash
npm run nano:am:session
npm run nano:appnext
# alias: npm run nano:am:appnext
npm run nano:appnext -- --app app-howto
npm run nano:test && npm run verify
```

## Artifacts

- Summary: `results/nano-lm/wave-am/appnext_summary.json`  
- One-pagers: [appnext-known.md](appnext-known.md) · [appnext-howto.md](appnext-howto.md) · [appnext-longdoc.md](appnext-longdoc.md) · [depl-am.md](depl-am.md)  
- Trials: `AM-APPNEXT-{KNOWN,HOWTO,LONGDOC}-{LOOKUP|GEN}-HITL-01…10`  
- Contract: `nano_lm/tests/test_appnext.py`

Next: **AM6 AM-HITL-10** — **DONE PROMOTE** → [wave-am-hitl.md](wave-am-hitl.md).
