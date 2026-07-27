# H-APPCORE — apps expose LOOKUP vs GENERATE (**DONE** — PROMOTE)

> Lab: `.local/pesquisa.md` §3 AO5 · Session: `.local/wave-ao/SESSION.md`  
> Parent: **H-FASTCORE** · **H-SMARTCORE** · Pack: AO0 held-out asks  
> Module: `nano_lm/src/appcore_ops.py` · Runner: `npm run nano:appcore` (`nano:ao:appcore`)

## Hypothesis

Package **3 AO0 surfaces** (known-ask · howto · long-doc) that **expose dual-arm** LOOKUP vs GENERATE with DEPL-AO honesty — ASK→EVAL→FIX×10 per surface; **GENCORE** grounded+extractive SERVE beyond APPPUSH mid-open; gen mean ≥ **5.0** **or** honest **HOLD**; never claim LOOKUP as generative IQ / peak as open-chat.

## Gate (Cursor ASK→EVAL→FIX×10 dual-arm / surface)

| Metric | Result | Pass bar / rule |
|--------|-------:|-----------------|
| apps packaged | **3** | ≥ 3 (known + howto + longdoc) |
| dual-arm expose | **3**/3 | LOOKUP + GENERATE labeled |
| LOOKUP mean across | **8.33** | ≥ **7.0** |
| GENERATE mean (SERVE) | **9.0** | ≥ **5.0** for PROMOTE else **HOLD** |
| vs APPPUSH SERVE gen 4.0 | **beat** (+5.0) | peak exact vs mid-open |
| peer APPEDGE SERVE gen 9.0 | **match** | AO-aware peak |
| DEPL pages ok | **4**/4 | 3 apps + [depl-ao.md](depl-ao.md) |
| FALSE_HIT | **0** | any → **KILL** |
| open-chat claim | **rejected** | DEPL honesty |
| Decision | **PROMOTE** | expose+lookup+gen≥5+DEPL |

## Frontier EVAL — per app

| App | Lookup mean | Gen mean (SERVE) | Dual-arm | Decision |
|-----|------------:|-----------------:|:--------:|----------|
| app-known | **8.3** | **9.0** | yes | **PROMOTE** |
| app-howto | **8.5** | **9.0** | yes | **PROMOTE** |
| app-longdoc | **8.2** | **9.0** | yes | **PROMOTE** |

LOOKUP = WRAP_LOOKUP TRUE_HIT / honest OOS refuse. GENERATE = QPFB2+GROUNDED+GENCORE_PEAK shared once · wall_ms>0 · peak spans (labeled ≠ open-chat IQ).

### Cursor EVAL bullets

1. In-scope SERVE gens are GENCORE extractive peak exact golds (e.g. `21`, `a.count(x)`, `while`) — not period collapse.  
2. OOS routes refuse honestly (not open chat).  
3. Dual-arm labels + DEPL-AO sync hold; SERVE gen **9.0** beats APPPUSH **4.0** → full PROMOTE.

## Finding

1. All three surfaces expose **LOOKUP vs GENERATE** with DEPL-AO dual-arm law documented.  
2. Lookup quality holds (mean **8.33**, false-hit **0**) — product retrieve path only.  
3. Generative SERVE mean **9.0** clears gen≥5 and peers APPEDGE via GENCORE peak stops.  
4. Ship claim remains **AF packaged stack** — next AO6 AO-HITL-10.

## Reproduce

```bash
npm run nano:ao:session
npm run nano:appcore
# alias: npm run nano:ao:appcore
npm run nano:appcore -- --app app-howto
npm run nano:test && npm run verify
```

## Artifacts

- Summary: `results/nano-lm/wave-ao/appcore_summary.json`  
- One-pagers: [appcore-known.md](appcore-known.md) · [appcore-howto.md](appcore-howto.md) · [appcore-longdoc.md](appcore-longdoc.md) · [depl-ao.md](depl-ao.md)  
- Trials: `AO-APPCORE-{KNOWN,HOWTO,LONGDOC}-{LOOKUP|GEN}-HITL-01…10`  
- Contract: `nano_lm/tests/test_appcore.py`

Next: **AO6 AO-HITL-10** — **DONE PROMOTE** → [wave-ao-hitl.md](wave-ao-hitl.md). Next **AO7 AO-REPORT**.
