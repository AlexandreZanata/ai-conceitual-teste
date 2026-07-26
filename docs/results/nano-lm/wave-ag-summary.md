# Wave AG — anti-FP dual-arm · real answers (**COMPLETE + FROZEN**)

> Lab: `.local/pesquisa.md` §5 · Paper-lab: [paper-lab-wave-ag.md](paper-lab-wave-ag.md) · HITL: [wave-ag-hitl.md](wave-ag-hitl.md) · Freeze: [ag-freeze.md](ag-freeze.md)  
> Parent: Wave AF **AF-FREEZE** reopen · Ship claim: **AF packaged stack** (unchanged)

**Status: COMPLETE + FROZEN** · Thesis: **Wave AG anti-FP dual-arm on 6th held-out pack: LOOKUP product ok; GENERATE below gen≥5 → documented HOLD; ship claim remains AF packaged stack — not open chat LM.**

## Stage scoreboard (Cursor ASK→EVAL→FIX dual-arm)

| # | ID | Lookup mean | Gen mean | Errors | FIX count | Decision | Note |
|---|-----|------------:|---------:|--------|----------:|----------|------|
| AG0 | **SESSION** | — | — | — | **0** | **PROMOTE** | freeze 10 held-out asks ≠ AB…AF |
| AG1 | **H-ANTIFP** | 9 | 1 | 0/4 | **0** | **PROMOTE** | harness: LOOKUP≠GEN labeled |
| AG2 | **H-CTXREAL** | 9 | 1 | 0/10 | **0** | **PROMOTE** | quad-doc L_eff↑ vs CTXULTRA |
| AG3 | **H-SMARTREAL** | 9 | 4 | 0/10 | **0** | **HOLD** | cite 10/10; gen<5 honest HOLD |
| AG4 | **H-FASTREAL** | 9 | 1 | 0/10 | **0** | **PROMOTE** | gen wall↓ vs AF raw; ≠ LOOKUP speed IQ |
| AG5 | **H-APPREAL** | 8.33 | 1 | 0/SERVE | **0** | **HOLD** | expose LOOKUP|GENERATE + DEPL-AG |
| AG6 | **AG-HITL-10** | 9 | 1 | 0/10 | **0** | **HOLD** | final dual-arm; ship claim=AF |
| AG7 | **AG-REPORT** | — | — | — | **0** | **PROMOTE** | public summary + paper-lab + anti-FP |
| AG8 | **AG-FREEZE** | — | — | — | **0** | **PROMOTE** | lock; no Wave AH invent |

## Anti-FP evidence (mandatory)

| Rule | Evidence |
|------|----------|
| LOOKUP labeled ≠ GENERATE | H-ANTIFP harness + every stage log |
| Generative arm `wall_ms>0` · `n_new>0` | CTXREAL · FASTREAL · AG-HITL-10 |
| Cursor scores **completion** (not auto TRUE_HIT→9 as IQ) | SMARTREAL gen 4.0 · final gen 1.0 |
| LOOKUP high score ≠ generative IQ | LOOKUP 9.0 / 8.33 with gen HOLD |
| LOOKUP scores are not generative IQ | dual-arm scoreboard + HOLD gates |
| No LOOKUP-only smarter-LM PROMOTE | SMARTREAL · APPREAL · AG-HITL-10 **HOLD** |

## Honest product claims

| Claim | Truth |
|-------|-------|
| Longer usable ctx (AG) | **H-CTXREAL** PROMOTE; L_eff↑ vs CTXULTRA |
| Smarter gen (AG) | **H-SMARTREAL** HOLD — gen **4.0** < 5 |
| Faster generative ask | **H-FASTREAL** PROMOTE — wall↓; LOOKUP ≠ speed IQ |
| Apps expose arms | **H-APPREAL** HOLD — DEPL-AG dual-arm |
| Final dual-arm HITL | **AG-HITL-10** LOOKUP **9.0** · GEN **1.0** · **HOLD** |
| Ship claim | **AF packaged stack** — not open chat |
| “Open chat LM ≤5M” | **False** — not open chat |

## Reproduce

```bash
npm run nano:ag:report
npm run nano:ag:session
npm run nano:antifp
npm run nano:ctxreal
npm run nano:smartreal
npm run nano:fastreal
npm run nano:appreal
npm run nano:ag:hitl
npm run nano:ag:freeze
```

## Do not reopen

QI · STREAM · KVCACHE-Q · GENCACHE · MIXD · GPFB-K=2 · naive CTX · ZPREF · claim LOOKUP = generative IQ · invent Wave AH without lab-book reopen · claim open chat.
