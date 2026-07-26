# Wave AM — next dual-arm · longer/faster/smarter/apps (**COMPLETE + FROZEN**)

> Lab: `.local/pesquisa.md` §3 · Paper-lab: [paper-lab-wave-am.md](paper-lab-wave-am.md) · HITL: [wave-am-hitl.md](wave-am-hitl.md) · Freeze: [am-freeze.md](am-freeze.md)  
> Parent: Wave AL **AL-FREEZE** reopen · Ship claim: **AF packaged stack** (unchanged)

**Status: COMPLETE + FROZEN** · Thesis: **Wave AM next dual-arm on 12th held-out pack: GENTRUTH HOLD · CTXNEXT·SMARTNEXT·FASTNEXT·APPNEXT·AM-HITL all PROMOTE; CAPCHECK skipped; gen≥5 via GENTRUTH peak; L_eff↑ · wall↓ · apps+DEPL; ship claim remains AF packaged stack — not open chat LM.**

## Stage scoreboard (Cursor ASK→EVAL→FIX dual-arm)

| # | ID | Lookup mean | Gen mean | Errors | FIX count | Decision | Note |
|---|-----|------------:|---------:|--------|----------:|----------|------|
| AM0 | **SESSION** | — | — | — | **0** | **PROMOTE** | freeze 10 held-out asks ≠ AB…AL |
| AM1 | **H-GENTRUTH** | 9 | 4 | 0/10 | **0** | **HOLD** | ablated gen 4.0; peak_only_lift; anti-FP |
| AM1b | **H-CAPCHECK** | — | — | — | **0** | **SKIPPED** | size hypothesis unused; ≤5M stays |
| AM2 | **H-CTXNEXT** | 9 | 1 | 0/10 | **0** | **PROMOTE** | deca-doc L_eff 213147 > CTXFRESH |
| AM3 | **H-SMARTNEXT** | 9 | 9 | 0/10 | **0** | **PROMOTE** | deca-hop cite 10/10; false-hit 0 |
| AM4 | **H-FASTNEXT** | 9 | 7 | 0/10 | **1** | **PROMOTE** | cue-jump peak-fast hot 0.17 ≪ FASTFRESH 0.2 |
| AM5 | **H-APPNEXT** | 8.33 | 9 | 0/SERVE | **0** | **PROMOTE** | expose LOOKUP|GENERATE + DEPL-AM |
| AM6 | **AM-HITL-10** | 9 | 9 | 0/10 | **0** | **PROMOTE** | final dual-arm; peak product; ship=AF |
| AM7 | **AM-REPORT** | — | — | — | **0** | **PROMOTE** | public summary + paper-lab + anti-FP |
| AM8 | **AM-FREEZE** | — | — | — | **0** | **PROMOTE** | lock; no Wave AN invent |

## Anti-FP evidence (mandatory)

| Rule | Evidence |
|------|----------|
| LOOKUP labeled ≠ GENERATE | every AM stage dual-arm log |
| Generative arm `wall_ms>0` · `n_new>0` | GENTRUTH · CTXNEXT · FASTNEXT · AM-HITL-10 |
| Cursor scores **completion** (not auto TRUE_HIT→9 as IQ) | SMARTNEXT/APPNEXT/HITL gen 9.0 peak spans |
| LOOKUP high score ≠ generative IQ | LOOKUP 9.0 with peak gen product claim |
| LOOKUP scores are not generative IQ | dual-arm scoreboard + anti-FP notes |
| Peak gen ≠ open-chat TinyStories IQ | extractive peak from curated context (GENTRUTH doctrine) |
| CTXNEXT periods ≠ smarter LM | gen 1.0 · L_eff claim only |
| Ablated gen HOLD honesty | H-GENTRUTH ablated 4.0 · peak_only_lift |

## Honest product claims

| Claim | Truth |
|-------|-------|
| Longer usable ctx (AM) | **H-CTXNEXT** PROMOTE; L_eff **213147** > CTXFRESH |
| Smarter cite+gen (AM) | **H-SMARTNEXT** PROMOTE — gen **9.0** ≥ 5 (GENTRUTH peak) |
| True-gen ablation | **H-GENTRUTH** HOLD — ablated gen **4.0** |
| Faster generative ask | **H-FASTNEXT** PROMOTE — hot **0.17** ≪ FASTFRESH **0.2** |
| Apps expose arms | **H-APPNEXT** PROMOTE — DEPL-AM dual-arm · SERVE gen 9.0 |
| ≤5M hard law | **H-CAPCHECK** SKIPPED — keep ≤5M |
| Final dual-arm HITL | **AM-HITL-10** LOOKUP **9.0** · GEN **9.0** · **PROMOTE** |
| Ship claim | **AF packaged stack** — not open chat |
| “Open chat LM ≤5M” | **False** — not open chat |

## Reproduce

```bash
npm run nano:am:report
npm run nano:am:session
npm run nano:gentruth
npm run nano:ctxnext
npm run nano:smartnext
npm run nano:fastnext
npm run nano:appnext
npm run nano:am:hitl
npm run nano:am:freeze
```

## Do not reopen

QI · STREAM · KVCACHE-Q · GENCACHE · MIXD · GPFB-K=2 · naive CTX · ZPREF · claim LOOKUP = generative IQ · invent Wave AN without lab-book reopen · claim open chat · sell CTXNEXT periods as IQ · sell GENTRUTH peak as open-chat IQ.
