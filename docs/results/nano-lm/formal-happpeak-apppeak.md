# H-APPPEAK — apps expose LOOKUP vs GENERATE (**DONE** — PROMOTE)

> Lab: `.local/pesquisa.md` §3 AJ5 · Session: `.local/wave-aj/SESSION.md`  
> Parent: **H-APPPUSH** · **H-FASTPEAK** · **H-GENPEAK** · Pack: AJ0 held-out asks  
> Module: `nano_lm/src/apppeak_ops.py` · Runner: `npm run nano:apppeak` (`nano:aj:apppeak`)

## Hypothesis

Package **3 AJ0 surfaces** (known-ask · howto · long-doc) that **expose dual-arm** LOOKUP vs GENERATE with DEPL-AJ honesty — ASK→EVAL→FIX×10 per surface; **GENPEAK** grounded+extractive SERVE beyond APPPUSH mid-open; gen mean ≥ **5.0** **or** honest **HOLD**; never claim LOOKUP as generative IQ.

## Gate (Cursor ASK→EVAL→FIX×10 dual-arm / surface)

| Metric | Result | Pass bar / rule |
|--------|-------:|-----------------|
| apps packaged | **3** | ≥ 3 (known + howto + longdoc) |
| dual-arm expose | **3**/3 | LOOKUP + GENERATE labeled |
| LOOKUP mean across | **8.33** | ≥ **7.0** |
| GENERATE mean (SERVE) | **9.0** | ≥ **5.0** for PROMOTE else **HOLD** |
| vs APPPUSH SERVE gen 4.0 | **beat** (+5.0) | peak exact vs mid-open |
| DEPL pages ok | **4**/4 | 3 apps + [depl-aj.md](depl-aj.md) |
| FALSE_HIT | **0** | any → **KILL** |
| open-chat claim | **rejected** | DEPL honesty |
| Decision | **PROMOTE** | expose+lookup+gen≥5+DEPL |

## Frontier EVAL — per app

| App | Lookup mean | Gen mean (SERVE) | Dual-arm | Decision |
|-----|------------:|-----------------:|:--------:|----------|
| app-known | **8.3** | **9.0** | yes | **PROMOTE** |
| app-howto | **8.5** | **9.0** | yes | **PROMOTE** |
| app-longdoc | **8.2** | **9.0** | yes | **PROMOTE** |

LOOKUP = WRAP_LOOKUP TRUE_HIT / honest OOS refuse. GENERATE = QPFB2+GROUNDED+PEAK shared once · wall_ms>0 · peak spans.

### Cursor EVAL bullets

1. In-scope SERVE gens are extractive peak exact golds (e.g. `32`, `P2WSH`, `collections.deque`) — not period collapse.  
2. OOS routes refuse honestly (not open chat).  
3. Dual-arm labels + DEPL-AJ sync hold; SERVE gen **9.0** beats APPPUSH **4.0** → full PROMOTE.

## Finding

1. All three surfaces expose **LOOKUP vs GENERATE** with DEPL-AJ dual-arm law documented.  
2. Lookup quality holds (mean **8.33**, false-hit **0**) — product retrieve path only.  
3. Generative SERVE mean **9.0** clears gen≥5 and beats APPPUSH **4.0** via GENPEAK peak stops.  
4. Ship claim remains **AF packaged stack** until AJ6.

## Reproduce

```bash
npm run nano:aj:session
npm run nano:apppeak
# alias: npm run nano:aj:apppeak
npm run nano:apppeak -- --app app-howto
npm run nano:test && npm run verify
```

## Artifacts

- Summary: `results/nano-lm/wave-aj/apppeak_summary.json`  
- One-pagers: [apppeak-known.md](apppeak-known.md) · [apppeak-howto.md](apppeak-howto.md) · [apppeak-longdoc.md](apppeak-longdoc.md) · [depl-aj.md](depl-aj.md)  
- Trials: `AJ-APPPEAK-{KNOWN,HOWTO,LONGDOC}-{LOOKUP|GEN}-HITL-01…10`  
- Contract: `nano_lm/tests/test_apppeak.py`

Next: **AJ6 AJ-HITL-10** (**DONE — PROMOTE** — [wave-aj-hitl.md](wave-aj-hitl.md)). Next: **AJ7 AJ-REPORT**.
