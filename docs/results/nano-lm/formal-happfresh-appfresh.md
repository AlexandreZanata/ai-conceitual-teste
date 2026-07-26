# H-APPFRESH — apps expose LOOKUP vs GENERATE (**DONE** — PROMOTE)

> Lab: `.local/pesquisa.md` §3 AL5 · Session: `.local/wave-al/SESSION.md`  
> Parent: **H-FASTFRESH** · **H-SMARTFRESH** · Pack: AL0 held-out asks  
> Module: `nano_lm/src/appfresh_ops.py` · Runner: `npm run nano:appfresh` (`nano:al:appfresh`)

## Hypothesis

Package **3 AL0 surfaces** (known-ask · howto · long-doc) that **expose dual-arm** LOOKUP vs GENERATE with DEPL-AL honesty — ASK→EVAL→FIX×10 per surface; **GENFRESH** grounded+extractive SERVE beyond APPPUSH mid-open; gen mean ≥ **5.0** **or** honest **HOLD**; never claim LOOKUP as generative IQ / peak as open-chat.

## Gate (Cursor ASK→EVAL→FIX×10 dual-arm / surface)

| Metric | Result | Pass bar / rule |
|--------|-------:|-----------------|
| apps packaged | **3** | ≥ 3 (known + howto + longdoc) |
| dual-arm expose | **3**/3 | LOOKUP + GENERATE labeled |
| LOOKUP mean across | **8.33** | ≥ **7.0** |
| GENERATE mean (SERVE) | **9.0** | ≥ **5.0** for PROMOTE else **HOLD** |
| vs APPPUSH SERVE gen 4.0 | **beat** (+5.0) | peak exact vs mid-open |
| peer APPMORE SERVE gen 9.0 | **match** | AL-aware peak |
| DEPL pages ok | **4**/4 | 3 apps + [depl-al.md](depl-al.md) |
| FALSE_HIT | **0** | any → **KILL** |
| open-chat claim | **rejected** | DEPL honesty |
| Decision | **PROMOTE** | expose+lookup+gen≥5+DEPL |

## Frontier EVAL — per app

| App | Lookup mean | Gen mean (SERVE) | Dual-arm | Decision |
|-----|------------:|-----------------:|:--------:|----------|
| app-known | **8.3** | **9.0** | yes | **PROMOTE** |
| app-howto | **8.5** | **9.0** | yes | **PROMOTE** |
| app-longdoc | **8.2** | **9.0** | yes | **PROMOTE** |

LOOKUP = WRAP_LOOKUP TRUE_HIT / honest OOS refuse. GENERATE = QPFB2+GROUNDED+GENFRESH_PEAK shared once · wall_ms>0 · peak spans (labeled ≠ open-chat IQ).

### Cursor EVAL bullets

1. In-scope SERVE gens are GENFRESH extractive peak exact golds (e.g. `24`, `a.reverse()`, `delattr`) — not period collapse.  
2. OOS routes refuse honestly (not open chat).  
3. Dual-arm labels + DEPL-AL sync hold; SERVE gen **9.0** beats APPPUSH **4.0** → full PROMOTE.

## Finding

1. All three surfaces expose **LOOKUP vs GENERATE** with DEPL-AL dual-arm law documented.  
2. Lookup quality holds (mean **8.33**, false-hit **0**) — product retrieve path only.  
3. Generative SERVE mean **9.0** clears gen≥5 and peers APPMORE via GENFRESH peak stops.  
4. Ship claim remains **AF packaged stack** until AL6.

## Reproduce

```bash
npm run nano:al:session
npm run nano:appfresh
# alias: npm run nano:al:appfresh
npm run nano:appfresh -- --app app-howto
npm run nano:test && npm run verify
```

## Artifacts

- Summary: `results/nano-lm/wave-al/appfresh_summary.json`  
- One-pagers: [appfresh-known.md](appfresh-known.md) · [appfresh-howto.md](appfresh-howto.md) · [appfresh-longdoc.md](appfresh-longdoc.md) · [depl-al.md](depl-al.md)  
- Trials: `AL-APPFRESH-{KNOWN,HOWTO,LONGDOC}-{LOOKUP|GEN}-HITL-01…10`  
- Contract: `nano_lm/tests/test_appfresh.py`

Next: **AL6 AL-HITL-10** — **DONE PROMOTE** → [wave-al-hitl.md](wave-al-hitl.md).
