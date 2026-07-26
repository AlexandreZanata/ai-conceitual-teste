# Wave AI — push dual-arm · longer/faster/smarter/apps (**COMPLETE + FROZEN**)

> Lab: `.local/pesquisa.md` §5 · Paper-lab: [paper-lab-wave-ai.md](paper-lab-wave-ai.md) · HITL: [wave-ai-hitl.md](wave-ai-hitl.md) · Freeze: [ai-freeze.md](ai-freeze.md)  
> Parent: Wave AH **AH-FREEZE** reopen · Ship claim: **AF packaged stack** (unchanged)

**Status: COMPLETE + FROZEN** · Thesis: **Wave AI push dual-arm on 8th held-out pack: CTXPUSH+FASTPUSH PROMOTE; GENPLUS/SMARTPUSH/APPPUSH/AI-HITL HOLD on gen<5; CAPRENEG HOLD keeps ≤5M; ship claim remains AF packaged stack — not open chat LM.**

## Stage scoreboard (Cursor ASK→EVAL→FIX dual-arm)

| # | ID | Lookup mean | Gen mean | Errors | FIX count | Decision | Note |
|---|-----|------------:|---------:|--------|----------:|----------|------|
| AI0 | **SESSION** | — | — | — | **0** | **PROMOTE** | freeze 10 held-out asks ≠ AB…AH |
| AI1 | **H-GENPLUS** | 9 | 4 | 0/10 | **0** | **HOLD** | grounded QPFB2; open mid 4.0 <5 |
| AI1b | **H-CAPRENEG** | 9 | 4 | 0/10 | **0** | **HOLD** | CAP-125M probe; keep ≤5M |
| AI2 | **H-CTXPUSH** | 9 | 1 | 0/10 | **0** | **PROMOTE** | hexa-doc L_eff 162851 > CTXLIFT |
| AI3 | **H-SMARTPUSH** | 9 | 4 | 0/10 | **0** | **HOLD** | hexa-hop cite 10/10; gen ties 4.0 |
| AI4 | **H-FASTPUSH** | 9 | 1 | 0/10 | **0** | **PROMOTE** | hot wall 10.7 < FASTLIFT 11.6 |
| AI5 | **H-APPPUSH** | 8.33 | 4 | 0/SERVE | **0** | **HOLD** | expose LOOKUP|GENERATE + DEPL-AI |
| AI6 | **AI-HITL-10** | 9 | 4 | 0/10 | **0** | **HOLD** | final dual-arm; ship claim=AF |
| AI7 | **AI-REPORT** | — | — | — | **0** | **PROMOTE** | public summary + paper-lab + anti-FP |
| AI8 | **AI-FREEZE** | — | — | — | **0** | **PROMOTE** | lock; no Wave AJ invent |

## Anti-FP evidence (mandatory)

| Rule | Evidence |
|------|----------|
| LOOKUP labeled ≠ GENERATE | every AI stage dual-arm log |
| Generative arm `wall_ms>0` · `n_new>0` | CTXPUSH · FASTPUSH · AI-HITL-10 |
| Cursor scores **completion** (not auto TRUE_HIT→9 as IQ) | GENPLUS/SMARTPUSH/APPPUSH gen 4.0 · final gen 4.0 |
| LOOKUP high score ≠ generative IQ | LOOKUP 9.0 / 8.33 with gen HOLD |
| LOOKUP scores are not generative IQ | dual-arm scoreboard + HOLD gates |
| No LOOKUP-only smarter-LM PROMOTE | GENPLUS · SMARTPUSH · APPPUSH · AI-HITL-10 **HOLD** |

## Honest product claims

| Claim | Truth |
|-------|-------|
| Longer usable ctx (AI) | **H-CTXPUSH** PROMOTE; L_eff **162851** > CTXLIFT |
| Smarter gen (AI) | **H-GENPLUS** / **H-SMARTPUSH** HOLD — gen **4.0** < 5 |
| Faster generative ask | **H-FASTPUSH** PROMOTE — hot **10.7** < FASTLIFT **11.6** |
| Apps expose arms | **H-APPPUSH** HOLD — DEPL-AI dual-arm · SERVE gen 4.0 |
| ≤5M hard law | **H-CAPRENEG** HOLD — keep ≤5M after CAP-125M |
| Final dual-arm HITL | **AI-HITL-10** LOOKUP **9.0** · GEN **4.0** · **HOLD** |
| Ship claim | **AF packaged stack** — not open chat |
| “Open chat LM ≤5M” | **False** — not open chat |

## Reproduce

```bash
npm run nano:ai:report
npm run nano:ai:session
npm run nano:genplus
npm run nano:capreneg
npm run nano:ctxpush
npm run nano:smartpush
npm run nano:fastpush
npm run nano:apppush
npm run nano:ai:hitl
npm run nano:ai:freeze
```

## Do not reopen

QI · STREAM · KVCACHE-Q · GENCACHE · MIXD · GPFB-K=2 · naive CTX · ZPREF · claim LOOKUP = generative IQ · invent Wave AJ without lab-book reopen · claim open chat.
