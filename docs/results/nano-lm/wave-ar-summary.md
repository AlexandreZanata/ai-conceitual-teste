# Wave AR — Product Science deepen + Nano Generative (**COMPLETE + FROZEN**)

> Lab: `.local/pesquisa.md` §5 · Paper-lab: [paper-lab-wave-ar.md](paper-lab-wave-ar.md) · HITL: [wave-ar-dual-hitl.md](wave-ar-dual-hitl.md) · Freeze: [ar-freeze.md](ar-freeze.md) · [formal-harfreeze-ar-freeze.md](formal-harfreeze-ar-freeze.md)  
> Parent: Wave AQ **AQ-FREEZE** reopen · Ship claim: **AF packaged stack + AQ product layer — not open chat LM**

**Status: COMPLETE + FROZEN** · Thesis: **Wave AR product deepen on AQ: ABSTAIN·SHIPDEMO PROMOTE; PARAEXT HOLD · ADVREG KILL · NANOGEN2 HOLD (ablated 4.3 · peak_only); AR-DUAL-HITL HOLD (soft deepen); generative/open-chat/mini-AGI locked; ship AF packaged stack + AQ product layer — not open chat LM.**

## Stage scoreboard (product deepen)

| # | ID | Metric | Decision | Note |
|---|-----|--------|----------|------|
| AR0 | **SESSION** | packs frozen | **PROMOTE** | ext-para · advreg · abstain · ship-demo · NANOGEN2 hyp |
| AR1 | **H-ABSTAIN** | OOD abstain 1.0 · FH 0 | **PROMOTE** | NO_ANSWER / ABSTAIN labeled |
| AR2 | **H-SHIPDEMO** | 4/4 modes visible | **PROMOTE** | LOOKUP · PEAK · DECODE · ABSTAIN |
| AR3 | **H-PARAEXT** | hit 0.65 < 0.70 | **HOLD** | FH 0 · misses reported · ≠ AQ-PARA |
| AR4 | **H-ADVREG** | false-hit 2/20 | **KILL** | SAFE≠quality documented · near-miss leaks |
| AR5 | **H-NANOGEN2** | ablated gen 4.3 | **HOLD** | beats NANOGEN 4.0 · peak/bank compare only |
| AR6 | **AR-DUAL-HITL** | core pass · soft deepen | **HOLD** | ABSTAIN/SHIPDEMO/apps · PARAEXT/ADVREG soft · gen locked |
| AR7 | **AR-REPORT** | summary + paper-lab | **PROMOTE** | docs + anti-FP table · real-eval |
| AR8 | **AR-FREEZE** | lock outcomes | **PROMOTE** | COMPLETE+FROZEN · no Wave AS invent |

## Anti-FP evidence (mandatory)

| Rule | Evidence |
|------|----------|
| LOOKUP labeled — not generative IQ | SHIPDEMO · DUAL-HITL apps · WRAP_LOOKUP |
| PEAK extractive ≠ open-chat | SHIPDEMO PEAK · NANOGEN2 peak compare only |
| DECODE arm `wall_ms>0` · `n_new>0` | SHIPDEMO DECODE · NANOGEN2 ablated |
| ABSTAIN refuse junk — not IQ | **H-ABSTAIN** OOD abstain **1.0** · FH **0** |
| SAFE ≠ answer quality | **H-ADVREG** SAFE≠quality · mean not sold as IQ |
| Ablated gen HOLD honesty | **H-NANOGEN2** ablated **4.3** · peak_only |
| Modes always visible | **H-SHIPDEMO** LOOKUP·PEAK·DECODE·ABSTAIN |
| Generative claim locked while HOLD | AR-DUAL-HITL · ship claim not open chat |
| Telemetry keys | `mode` · `wall_ms` · `n_new` · `product_mode` |

## Honest product claims

| Claim | Truth |
|-------|-------|
| Refuse junk DECODE | **H-ABSTAIN** PROMOTE — OOD abstain **1.0** |
| Mode-visible ship/demo | **H-SHIPDEMO** PROMOTE — 4/4 |
| External paraphrase | **H-PARAEXT** HOLD — hit **0.65** < 0.70 · FH **0** |
| Adversary regression | **H-ADVREG** KILL — false-hit **2**/20 · SAFE≠quality |
| North-star generative | **H-NANOGEN2** HOLD — ablated **4.3** · not open chat |
| Final dual HITL | **AR-DUAL-HITL** HOLD — core pass · soft deepen · gen locked |
| Ship claim | **AF packaged stack + AQ product layer — not open chat LM** |
| “Open chat / mini-AGI ≤5M” | **False** — AR5 HOLD |

## Real-eval section

| Arm | What was measured | Outcome |
|-----|-------------------|---------|
| Product core | ABSTAIN · SHIPDEMO · apps LOOKUP | **PROMOTE / PASS** |
| Product deepen | PARAEXT · ADVREG | **HOLD / KILL** (honest soft) |
| Generative | NANOGEN2 ablated vs NANOGEN 4.0 | **HOLD** (4.3 < 5.0) |
| Dual HITL | composite + claim honesty | **HOLD** · gen claim locked |

## Reproduce

```bash
npm run nano:ar:report
npm run nano:ar:session
npm run nano:abstain
npm run nano:shipdemo
npm run nano:paraext
npm run nano:advreg
npm run nano:nanogen2
npm run nano:ar:dual-hitl
```

## Do not reopen

QI · STREAM · KVCACHE-Q · GENCACHE · MIXD · GPFB-K=2 · naive CTX · ZPREF · claim LOOKUP = generative IQ · invent Wave AS without lab-book reopen · claim open chat / mini-AGI while H-NANOGEN2 HOLD · sell PEAK/bank-grounded as open-chat IQ · sell SAFE mean as IQ · sell product soft HOLD as generative unlock.
