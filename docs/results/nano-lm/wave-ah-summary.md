# Wave AH — lift dual-arm · longer/faster/apps (**COMPLETE + FROZEN**)

> Lab: `.local/pesquisa.md` §5 · Paper-lab: [paper-lab-wave-ah.md](paper-lab-wave-ah.md) · HITL: [wave-ah-hitl.md](wave-ah-hitl.md) · Freeze: [ah-freeze.md](ah-freeze.md)  
> Parent: Wave AG **AG-FREEZE** reopen · Ship claim: **AF packaged stack** (unchanged)

**Status: COMPLETE + FROZEN** · Thesis: **Wave AH lift dual-arm on 7th held-out pack: CTXLIFT+FASTLIFT PROMOTE; GENLIFT/SMARTLIFT/APPLIFT/AH-HITL HOLD on gen<5; ship claim remains AF packaged stack — not open chat LM.**

## Stage scoreboard (Cursor ASK→EVAL→FIX dual-arm)

| # | ID | Lookup mean | Gen mean | Errors | FIX count | Decision | Note |
|---|-----|------------:|---------:|--------|----------:|----------|------|
| AH0 | **SESSION** | — | — | — | **0** | **PROMOTE** | freeze 10 held-out asks ≠ AB…AG |
| AH1 | **H-GENLIFT** | 9 | 4 | 0/10 | **0** | **HOLD** | anti-period; open mid 4.0 <5 |
| AH2 | **H-CTXLIFT** | 9 | 1 | 0/10 | **0** | **PROMOTE** | penta-doc L_eff↑ vs CTXREAL |
| AH3 | **H-SMARTLIFT** | 9 | 4 | 0/10 | **0** | **HOLD** | cite 10/10; gen ties SMARTREAL 4.0 |
| AH4 | **H-FASTLIFT** | 9 | 1 | 0/10 | **0** | **PROMOTE** | hot wall 11.6 < FASTREAL 16.1 |
| AH5 | **H-APPLIFT** | 8.33 | 1 | 0/SERVE | **0** | **HOLD** | expose LOOKUP|GENERATE + DEPL-AH |
| AH6 | **AH-HITL-10** | 9 | 1 | 0/10 | **0** | **HOLD** | final dual-arm; ship claim=AF |
| AH7 | **AH-REPORT** | — | — | — | **0** | **PROMOTE** | public summary + paper-lab + anti-FP |
| AH8 | **AH-FREEZE** | — | — | — | **0** | **PROMOTE** | lock; no Wave AI invent |

## Anti-FP evidence (mandatory)

| Rule | Evidence |
|------|----------|
| LOOKUP labeled ≠ GENERATE | every AH stage dual-arm log |
| Generative arm `wall_ms>0` · `n_new>0` | CTXLIFT · FASTLIFT · AH-HITL-10 |
| Cursor scores **completion** (not auto TRUE_HIT→9 as IQ) | GENLIFT/SMARTLIFT gen 4.0 · final gen 1.0 |
| LOOKUP high score ≠ generative IQ | LOOKUP 9.0 / 8.33 with gen HOLD |
| LOOKUP scores are not generative IQ | dual-arm scoreboard + HOLD gates |
| No LOOKUP-only smarter-LM PROMOTE | GENLIFT · SMARTLIFT · APPLIFT · AH-HITL-10 **HOLD** |

## Honest product claims

| Claim | Truth |
|-------|-------|
| Longer usable ctx (AH) | **H-CTXLIFT** PROMOTE; L_eff **111578** > CTXREAL |
| Smarter gen (AH) | **H-GENLIFT** / **H-SMARTLIFT** HOLD — gen **4.0** < 5 |
| Faster generative ask | **H-FASTLIFT** PROMOTE — hot **11.6** < FASTREAL **16.1** |
| Apps expose arms | **H-APPLIFT** HOLD — DEPL-AH dual-arm |
| Final dual-arm HITL | **AH-HITL-10** LOOKUP **9.0** · GEN **1.0** · **HOLD** |
| Ship claim | **AF packaged stack** — not open chat |
| “Open chat LM ≤5M” | **False** — not open chat |

## Reproduce

```bash
npm run nano:ah:report
npm run nano:ah:session
npm run nano:genlift
npm run nano:ctxlift
npm run nano:smartlift
npm run nano:fastlift
npm run nano:applift
npm run nano:ah:hitl
npm run nano:ah:freeze
```

## Do not reopen

QI · STREAM · KVCACHE-Q · GENCACHE · MIXD · GPFB-K=2 · naive CTX · ZPREF · claim LOOKUP = generative IQ · invent Wave AI without lab-book reopen · claim open chat.
