# H-APPPUSH — apps expose LOOKUP vs GENERATE (**DONE** — HOLD)

> Lab: `.local/pesquisa.md` §5 AI5 · Session: `.local/wave-ai/SESSION.md`  
> Parent: **H-APPLIFT** · **H-FASTPUSH** · Pack: AI0 held-out asks  
> Module: `nano_lm/src/apppush_ops.py` · Runner: `npm run nano:apppush` (`nano:ai:apppush`)

## Hypothesis

Package **3 AI0 surfaces** (known-ask · howto · long-doc) that **expose dual-arm** LOOKUP vs GENERATE with DEPL-AI honesty — ASK→EVAL→FIX×10 per surface; grounded GENERATE push beyond APPLIFT periods; gen mean ≥ **5.0** **or** honest **HOLD**; never claim LOOKUP as generative IQ.

## Gate (Cursor ASK→EVAL→FIX×10 dual-arm / surface)

| Metric | Result | Pass bar / rule |
|--------|-------:|-----------------|
| apps packaged | **3** | ≥ 3 (known + howto + longdoc) |
| dual-arm expose | **3**/3 | LOOKUP + GENERATE labeled |
| LOOKUP mean across | **8.33** | ≥ **7.0** |
| GENERATE mean (SERVE) | **4.0** | ≥ **5.0** for PROMOTE else **HOLD** |
| vs APPLIFT SERVE gen 1.0 | **beat** (+3.0) | grounded mid vs periods |
| DEPL pages ok | **4**/4 | 3 apps + [depl-ai.md](depl-ai.md) |
| FALSE_HIT | **0** | any → **KILL** |
| open-chat claim | **rejected** | DEPL honesty |
| Decision | **HOLD** | expose+lookup+DEPL ok; gen &lt; 5 (honest) |

## Frontier EVAL — per app

| App | Lookup mean | Gen mean (SERVE) | Dual-arm | Decision |
|-----|------------:|-----------------:|:--------:|----------|
| app-known | **8.3** | **4.0** | yes | **HOLD** |
| app-howto | **8.5** | **4.0** | yes | **HOLD** |
| app-longdoc | **8.2** | **4.0** | yes | **HOLD** |

LOOKUP = WRAP_LOOKUP TRUE_HIT / honest OOS refuse. GENERATE = QPFB2+GROUNDED shared once · wall_ms&gt;0 · mid open (not gold).

### Cursor EVAL bullets

1. In-scope SERVE gens are non-period TinyStories drift — mid **4.0**, not curated golds.  
2. OOS routes refuse honestly (not open chat).  
3. Dual-arm labels + DEPL-AI sync hold — PROMOTE blocked only by gen&lt;5; beats APPLIFT periods.

## Finding

1. All three surfaces expose **LOOKUP vs GENERATE** with DEPL-AI dual-arm law documented.  
2. Lookup quality holds (mean **8.33**, false-hit **0**) — product retrieve path only.  
3. Generative SERVE mean **4.0** beats APPLIFT **1.0** but stays below gen≥5 → **HOLD** per §5 AI5.  
4. Ship claim remains **AF packaged stack** until AI6.

## Reproduce

```bash
npm run nano:ai:session
npm run nano:apppush
# alias: npm run nano:ai:apppush
npm run nano:apppush -- --app app-howto
npm run nano:test && npm run verify
```

## Artifacts

- Summary: `results/nano-lm/wave-ai/apppush_summary.json`  
- One-pagers: [apppush-known.md](apppush-known.md) · [apppush-howto.md](apppush-howto.md) · [apppush-longdoc.md](apppush-longdoc.md) · [depl-ai.md](depl-ai.md)  
- Trials: `AI-APPPUSH-{KNOWN,HOWTO,LONGDOC}-{LOOKUP\|GEN}-HITL-01…10`  
- Contract: `nano_lm/tests/test_apppush.py`

Next: **AI6 AI-HITL-10**.
