# Wave AJ — peak dual-arm · longer/faster/smarter/apps (**COMPLETE + FROZEN**)

> Lab: `.local/pesquisa.md` §3 · Paper-lab: [paper-lab-wave-aj.md](paper-lab-wave-aj.md) · HITL: [wave-aj-hitl.md](wave-aj-hitl.md) · Freeze: [aj-freeze.md](aj-freeze.md)  
> Parent: Wave AI **AI-FREEZE** reopen · Ship claim: **AF packaged stack** (unchanged)

**Status: COMPLETE + FROZEN** · Thesis: **Wave AJ peak dual-arm on 9th held-out pack: GENPEAK·CTXPEAK·SMARTPEAK·FASTPEAK·APPPEAK·AJ-HITL all PROMOTE; CAPCHECK skipped; gen≥5 via grounded extractive peak; ship claim remains AF packaged stack — not open chat LM.**

## Stage scoreboard (Cursor ASK→EVAL→FIX dual-arm)

| # | ID | Lookup mean | Gen mean | Errors | FIX count | Decision | Note |
|---|-----|------------:|---------:|--------|----------:|----------|------|
| AJ0 | **SESSION** | — | — | — | **0** | **PROMOTE** | freeze 10 held-out asks ≠ AB…AI |
| AJ1 | **H-GENPEAK** | 9 | 9 | 0/10 | **0** | **PROMOTE** | grounded+extractive peak; gen≥5 |
| AJ1b | **H-CAPCHECK** | — | — | — | **0** | **SKIPPED** | gen≥5 without size reopen; ≤5M stays |
| AJ2 | **H-CTXPEAK** | 9 | 1 | 0/10 | **0** | **PROMOTE** | hepta-doc L_eff 177809 > CTXPUSH |
| AJ3 | **H-SMARTPEAK** | 9 | 9 | 0/10 | **0** | **PROMOTE** | hepta-hop cite 10/10; gen 9.0 > SMARTPUSH |
| AJ4 | **H-FASTPEAK** | 9 | 7 | 0/10 | **0** | **PROMOTE** | peak-fast hot ~5.0ms < FASTPUSH 10.7 |
| AJ5 | **H-APPPEAK** | 8.33 | 9 | 0/SERVE | **0** | **PROMOTE** | expose LOOKUP|GENERATE + DEPL-AJ |
| AJ6 | **AJ-HITL-10** | 9 | 9 | 0/10 | **0** | **PROMOTE** | final dual-arm; peak product; ship=AF |
| AJ7 | **AJ-REPORT** | — | — | — | **0** | **PROMOTE** | public summary + paper-lab + anti-FP |
| AJ8 | **AJ-FREEZE** | — | — | — | **0** | **PROMOTE** | lock; no Wave AK invent |

## Anti-FP evidence (mandatory)

| Rule | Evidence |
|------|----------|
| LOOKUP labeled ≠ GENERATE | every AJ stage dual-arm log |
| Generative arm `wall_ms>0` · `n_new>0` | GENPEAK · CTXPEAK · FASTPEAK · AJ-HITL-10 |
| Cursor scores **completion** (not auto TRUE_HIT→9 as IQ) | GENPEAK/SMARTPEAK/APPPEAK/HITL gen 9.0 peak spans |
| LOOKUP high score ≠ generative IQ | LOOKUP 9.0 with peak gen product claim |
| LOOKUP scores are not generative IQ | dual-arm scoreboard + anti-FP notes |
| Peak gen ≠ open-chat TinyStories IQ | extractive peak from curated context (GENPEAK doctrine) |
| CTXPEAK periods ≠ smarter LM | gen 1.0 · L_eff claim only |

## Honest product claims

| Claim | Truth |
|-------|-------|
| Longer usable ctx (AJ) | **H-CTXPEAK** PROMOTE; L_eff **177809** > CTXPUSH |
| Smarter gen (AJ) | **H-GENPEAK** / **H-SMARTPEAK** PROMOTE — gen **9.0** ≥ 5 (grounded peak) |
| Faster generative ask | **H-FASTPEAK** PROMOTE — hot **~5.0** < FASTPUSH **10.7** |
| Apps expose arms | **H-APPPEAK** PROMOTE — DEPL-AJ dual-arm · SERVE gen 9.0 |
| ≤5M hard law | **H-CAPCHECK** SKIPPED — keep ≤5M |
| Final dual-arm HITL | **AJ-HITL-10** LOOKUP **9.0** · GEN **9.0** · **PROMOTE** |
| Ship claim | **AF packaged stack** — not open chat |
| “Open chat LM ≤5M” | **False** — not open chat |

## Reproduce

```bash
npm run nano:aj:report
npm run nano:aj:session
npm run nano:genpeak
npm run nano:ctxpeak
npm run nano:smartpeak
npm run nano:fastpeak
npm run nano:apppeak
npm run nano:aj:hitl
npm run nano:aj:freeze
```

## Do not reopen

QI · STREAM · KVCACHE-Q · GENCACHE · MIXD · GPFB-K=2 · naive CTX · ZPREF · claim LOOKUP = generative IQ · invent Wave AK without lab-book reopen · claim open chat · sell CTXPEAK periods as IQ.
