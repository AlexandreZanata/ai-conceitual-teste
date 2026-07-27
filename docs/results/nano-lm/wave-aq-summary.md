# Wave AQ — Product Science + Nano Generative (**COMPLETE**)

> Lab: `.local/pesquisa.md` §5 · Paper-lab: [paper-lab-wave-aq.md](paper-lab-wave-aq.md) · HITL: [wave-aq-product-hitl.md](wave-aq-product-hitl.md) · Freeze: [aq-freeze.md](aq-freeze.md) (pending AQ9)  
> Parent: Wave AP **AP-FREEZE** reopen · Ship claim: **AF packaged stack + AQ product layer — not open chat LM**

**Status: COMPLETE** (freeze pending AQ9) · Thesis: **Wave AQ product science on AF: PARAHIT·ADVFP·LATP·KBCOV·MODEUI·PRODUCT-HITL PROMOTE; H-NANOGEN HOLD (ablated 4.0 · peak_only_lift); generative/open-chat/mini-AGI claims locked; ship AF packaged stack + AQ product layer — not open chat LM.**

## Stage scoreboard (product science)

| # | ID | Metric | Decision | Note |
|---|-----|--------|----------|------|
| AQ0 | **SESSION** | packs frozen | **PROMOTE** | para-20 · adv-20 · latency · KB · mode charter |
| AQ1 | **H-PARAHIT** | hit_rate 0.95 · mean 8.75 | **PROMOTE** | false-hit 0 · SEMWRAP paraphrase |
| AQ2 | **H-ADVFP** | false-hit 0/20 | **PROMOTE** | near-miss · OOD · trap SAFE |
| AQ3 | **H-LATP** | PEAK p50 0.0223 | **PROMOTE** | ≤ FASTBASE hot 0.0471 · triad published |
| AQ4 | **H-KBCOV** | coverage 100% (22/22) | **PROMOTE** | 6 product holes · no fake complete KB |
| AQ5 | **H-MODEUI** | 3/3 modes visible | **PROMOTE** | LOOKUP · PEAK · DECODE |
| AQ6 | **H-NANOGEN** | ablated gen 4.0 | **HOLD** | peak_only_lift · gen claim locked |
| AQ7 | **AQ-PRODUCT-HITL** | pillars + apps | **PROMOTE** | product PROMOTE · gen locked |
| AQ8 | **AQ-REPORT** | summary + paper-lab | **PROMOTE** | docs + anti-FP table |
| AQ9 | **AQ-FREEZE** | lock outcomes | **pending** | stub until AQ9 · no Wave AR invent |

## Anti-FP evidence (mandatory)

| Rule | Evidence |
|------|----------|
| LOOKUP labeled — not generative IQ | PARAHIT · PRODUCT-HITL · MODEUI `mode=LOOKUP` |
| PEAK extractive ≠ open-chat | LATP · MODEUI PEAK · NANOGEN peak compare only |
| DECODE arm `wall_ms>0` · `n_new>0` | LATP DECODE · MODEUI DECODE · NANOGEN ablated |
| LOOKUP high score — not generative IQ | PARAHIT 0.95 · LOOKUP mean 9.0 with gen HOLD |
| Ablated gen HOLD honesty | **H-NANOGEN** ablated **4.0** · peak_only_lift |
| Modes always visible | **H-MODEUI** LOOKUP·PEAK·DECODE |
| Generative claim locked while HOLD | AQ-PRODUCT-HITL · ship claim not open chat |
| Telemetry keys | `mode` · `wall_ms` · `n_new` · `product_mode` |

## Honest product claims

| Claim | Truth |
|-------|-------|
| Paraphrase robustness | **H-PARAHIT** PROMOTE — hit_rate **0.95** · false-hit **0** |
| Adversary safety | **H-ADVFP** PROMOTE — false-hit **0**/20 |
| Latency triad published | **H-LATP** PROMOTE — PEAK p50 **0.0223** ≤ FASTBASE hot |
| KB coverage honest | **H-KBCOV** PROMOTE — 100% registry + **6** product holes |
| Mode-visible UI | **H-MODEUI** PROMOTE — 3/3 |
| North-star generative | **H-NANOGEN** HOLD — ablated **4.0** · not open chat |
| Final product HITL | **AQ-PRODUCT-HITL** PROMOTE — gen claim locked |
| Ship claim | **AF packaged stack + AQ product layer — not open chat LM** |
| “Open chat / mini-AGI ≤5M” | **False** — AQ6 HOLD |

## Reproduce

```bash
npm run nano:aq:report
npm run nano:aq:session
npm run nano:parahit
npm run nano:advfp
npm run nano:latp
npm run nano:kbcov
npm run nano:modeui
npm run nano:nanogen
npm run nano:aq:product-hitl
# next: npm run nano:aq:freeze (AQ9)
```

## Do not reopen

QI · STREAM · KVCACHE-Q · GENCACHE · MIXD · GPFB-K=2 · naive CTX · ZPREF · claim LOOKUP = generative IQ · invent Wave AR without lab-book reopen · claim open chat / mini-AGI while H-NANOGEN HOLD · sell PEAK as open-chat IQ · sell product PROMOTE as generative unlock.
