# H-APPMORE — apps expose LOOKUP vs GENERATE (**DONE** — PROMOTE)

> Lab: `.local/pesquisa.md` §3 AK5 · Session: `.local/wave-ak/SESSION.md`  
> Parent: **H-FASTMORE** · **H-SMARTMORE** · Pack: AK0 held-out asks  
> Module: `nano_lm/src/appmore_ops.py` · Runner: `npm run nano:appmore` (`nano:ak:appmore`)

## Hypothesis

Package **3 AK0 surfaces** (known-ask · howto · long-doc) that **expose dual-arm** LOOKUP vs GENERATE with DEPL-AK honesty — ASK→EVAL→FIX×10 per surface; **GENTRUE** grounded+extractive SERVE beyond APPPUSH mid-open; gen mean ≥ **5.0** **or** honest **HOLD**; never claim LOOKUP as generative IQ / peak as open-chat.

## Gate (Cursor ASK→EVAL→FIX×10 dual-arm / surface)

| Metric | Result | Pass bar / rule |
|--------|-------:|-----------------|
| apps packaged | **3** | ≥ 3 (known + howto + longdoc) |
| dual-arm expose | **3**/3 | LOOKUP + GENERATE labeled |
| LOOKUP mean across | **8.33** | ≥ **7.0** |
| GENERATE mean (SERVE) | **9.0** | ≥ **5.0** for PROMOTE else **HOLD** |
| vs APPPUSH SERVE gen 4.0 | **beat** (+5.0) | peak exact vs mid-open |
| DEPL pages ok | **4**/4 | 3 apps + [depl-ak.md](depl-ak.md) |
| FALSE_HIT | **0** | any → **KILL** |
| open-chat claim | **rejected** | DEPL honesty |
| Decision | **PROMOTE** | expose+lookup+gen≥5+DEPL |

## Frontier EVAL — per app

| App | Lookup mean | Gen mean (SERVE) | Dual-arm | Decision |
|-----|------------:|-----------------:|:--------:|----------|
| app-known | **8.3** | **9.0** | yes | **PROMOTE** |
| app-howto | **8.5** | **9.0** | yes | **PROMOTE** |
| app-longdoc | **8.2** | **9.0** | yes | **PROMOTE** |

LOOKUP = WRAP_LOOKUP TRUE_HIT / honest OOS refuse. GENERATE = QPFB2+GROUNDED+GENTRUE_PEAK shared once · wall_ms>0 · peak spans (labeled ≠ open-chat IQ).

### Cursor EVAL bullets

1. In-scope SERVE gens are GENTRUE extractive peak exact golds (e.g. `128-256`, `a.clear()`, `bool`) — not period collapse.  
2. OOS routes refuse honestly (not open chat).  
3. Dual-arm labels + DEPL-AK sync hold; SERVE gen **9.0** beats APPPUSH **4.0** → full PROMOTE.

## Finding

1. All three surfaces expose **LOOKUP vs GENERATE** with DEPL-AK dual-arm law documented.  
2. Lookup quality holds (mean **8.33**, false-hit **0**) — product retrieve path only.  
3. Generative SERVE mean **9.0** clears gen≥5 and beats APPPUSH **4.0** via GENTRUE peak stops.  
4. Ship claim remains **AF packaged stack** until AK6.

## Reproduce

```bash
npm run nano:ak:session
npm run nano:appmore
# alias: npm run nano:ak:appmore
npm run nano:appmore -- --app app-howto
npm run nano:test && npm run verify
```

## Artifacts

- Summary: `results/nano-lm/wave-ak/appmore_summary.json`  
- One-pagers: [appmore-known.md](appmore-known.md) · [appmore-howto.md](appmore-howto.md) · [appmore-longdoc.md](appmore-longdoc.md) · [depl-ak.md](depl-ak.md)  
- Trials: `AK-APPMORE-{KNOWN,HOWTO,LONGDOC}-{LOOKUP|GEN}-HITL-01…10`  
- Contract: `nano_lm/tests/test_appmore.py`

Next: **AK6 AK-HITL-10** — **DONE PROMOTE** → [wave-ak-hitl.md](wave-ak-hitl.md).
