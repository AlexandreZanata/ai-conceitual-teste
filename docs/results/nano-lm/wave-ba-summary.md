# Wave BA — forever anti-FP + Nano gen-defer honesty (**COMPLETE + FROZEN**)

> Lab: `.local/pesquisa.md` §8 · Paper-lab: [paper-lab-wave-ba.md](paper-lab-wave-ba.md) · Real-eval: [wave-ba-real-eval.md](wave-ba-real-eval.md) · Freeze: [ba-freeze.md](ba-freeze.md) · [formal-habfreeze-ba-freeze.md](formal-habfreeze-ba-freeze.md)  
> Parent: Wave AZ **AZ-FREEZE** · Ship claim: **AF packaged stack + AQ product layer + AS trust path + ablated DECODE (snippet-prefix + gibberish-tail STRICT) — not unlabeled open chat LM · not TAC unlocked**

**Status: COMPLETE + FROZEN** · Thesis: **Wave BA dual track: H-REALGAIN·H-FASTREAL·H-CTXREAL2 PROMOTE (forever FH 0 · prod p50/p99 · howto·cite·long content · anti-FP); H-NANOGEN11 DEFER (gen stance defer · CAPCHECK closed · NANOGEN6·7 HOLD · NANOGEN8·9·10 DEFER cited · not NANOGEN10 rename); BA-REAL-EVAL PROMOTE (live battery 10/10 · forever FP ABSTAIN · over-refuse LOOKUP · gen locked); ship AF packaged stack + AQ product layer + AS trust path + ablated DECODE (snippet-prefix + gibberish-tail STRICT) — not unlabeled open chat LM · not TAC unlocked.**

## Stage scoreboard (product + generative)

| # | ID | Metric | Decision | Note |
|---|-----|--------|----------|------|
| BA0 | **SESSION** | packs frozen | **PROMOTE** | BA-FOREVER · AZ hold · §1 scoreboard · gen stance defer · true-eval |
| BA1 | **H-REALGAIN** | forever FH 0 · live FP 0 | **PROMOTE** | forever FH 0 · AZ hold 0 · over-refuse 0 · live probes · no bank stuffing |
| BA2 | **H-FASTREAL** | prod p50/p99 no FP regress | **PROMOTE** | prod latency published · anti-FP hold · ≠ AG nano:fastreal archive |
| BA3 | **H-CTXREAL2** | howto·cite·long content_ok | **PROMOTE** | content bars · anti-FP hold · L_eff alone ≠ win · ≠ AG nano:ctxreal |
| BA4 | **H-NANOGEN11** | gen stance defer | **DEFER** | CAPCHECK closed · no real M1|M2|M3 · NANOGEN6·7 HOLD · NANOGEN8·9·10 DEFER · not rename |
| BA5 | **BA-REAL-EVAL** | live ask battery 10/10 | **PROMOTE** | product+ctx+speed pass · forever ABSTAIN · over-refuse LOOKUP · gen locked · prod=eval |
| BA6 | **BA-REPORT** | summary + paper-lab | **PROMOTE** | docs + anti-FP · BA4 DEFER · NANOGEN6/7 HOLD · NANOGEN8·9·10 DEFER cited |
| BA7 | **BA-FREEZE** | lock outcomes | **PROMOTE** | COMPLETE+FROZEN · no Wave BB invent |

## Anti-FP evidence (mandatory)

| Rule | Evidence |
|------|----------|
| LOOKUP labeled — not generative IQ | H-REALGAIN · BA-REAL-EVAL known_lookup · WRAP_LOOKUP |
| PEAK extractive ≠ open-chat | BA-REAL-EVAL PEAK · H-CTXREAL2 usable span |
| DECODE arm `wall_ms>0` · `n_new>0` | BA-ASK-05 DECODE path · junk law |
| DECODE gibberish ≠ content_ok | BA-ASK-06 junk→ABSTAIN |
| Forever intent LOOKUP = false-hit | H-REALGAIN forever FH 0 · BA-ASK-07/10 ABSTAIN |
| Exact-gold ABSTAIN = product miss | H-REALGAIN over-refuse 0 · BA-ASK-08 LOOKUP |
| ABSTAIN refuse junk / OOD / near-miss / forever | BA-REAL-EVAL OOD·junk·near-miss·forever·AZ hold · FH 0 |
| SAFE ≠ answer quality | H-REALGAIN cites SAFE≠quality |
| True-gen DEFER honesty | **H-NANOGEN11** DEFER · **H-NANOGEN10** DEFER · **H-NANOGEN9** DEFER · **H-NANOGEN8** DEFER · **H-NANOGEN6** HOLD · **H-NANOGEN7** HOLD · true_continue unmet · span-fallback ≠ gen IQ · not unlabeled open chat |
| Modes always visible + content bars | **H-CTXREAL2** · **BA-REAL-EVAL** LOOKUP·PEAK·DECODE·ABSTAIN |
| Speed without FP regress | **H-FASTREAL** prod p50/p99 · anti-FP hold |
| Generative claim gated | BA-REAL-EVAL · unlock only if BA4 PROMOTE |
| Telemetry keys | `mode` · `wall_ms` · `n_new` · `product_mode` |

## Honest claims

| Claim | Truth |
|-------|-------|
| Forever anti-FP scoreboard | **H-REALGAIN** PROMOTE |
| Prod speed p50/p99 | **H-FASTREAL** PROMOTE |
| Ctx howto·cite·long content | **H-CTXREAL2** PROMOTE |
| North-star generative | **H-NANOGEN11** DEFER — stance defer · CAPCHECK closed · NANOGEN6·7 HOLD · NANOGEN8·9·10 DEFER stand · not rename |
| Parent gen HOLDs / DEFER cited | **H-NANOGEN6** HOLD · **H-NANOGEN7** HOLD · **H-NANOGEN8** DEFER · **H-NANOGEN9** DEFER · **H-NANOGEN10** DEFER |
| Final real eval | **BA-REAL-EVAL** PROMOTE — battery **10/10** · forever ABSTAIN · over-refuse LOOKUP · gen locked |
| Ship claim | **AF packaged stack + AQ product layer + AS trust path + ablated DECODE (snippet-prefix + gibberish-tail STRICT) — not unlabeled open chat LM · not TAC unlocked** |
| “Unlabeled open chat / GPT-class ≤5M” | **False** |
| “TAC / true-continue unlocked” | **False** (BA4 DEFER) |
| “Mini-AGI unlocked” | **False** (BA4 DEFER) |

## Real-eval section

| Arm | What was measured | Outcome |
|-----|-------------------|---------|
| Product (REALGAIN) | forever FH 0 · AZ hold · over-refuse 0 · live FP 0 | **PROMOTE** |
| Speed (FASTREAL) | prod p50/p99 · anti-FP hold | **PROMOTE** |
| Context (CTXREAL2) | howto·cite·long content_ok · anti-FP hold | **PROMOTE** |
| Generative (NANOGEN11) | defer stance · CAPCHECK closed · cite NANOGEN6·7 HOLD · NANOGEN8·9·10 DEFER · not rename | **DEFER** |
| Live ask battery | LOOKUP·PEAK·DECODE·ABSTAIN + forever FP · over-refuse · near-miss · DECODE junk→ABSTAIN | **PASS** 10/10 |

## Reproduce

```bash
npm run nano:ba:report
npm run nano:ba:session
npm run nano:realgain
npm run nano:ba:fastreal
npm run nano:ba:ctxreal2
npm run nano:nanogen11
npm run nano:ba:real-eval
```

## Do not reopen

QI · STREAM · KVCACHE-Q · GENCACHE · MIXD · GPFB-K=2 · naive CTX · ZPREF · claim LOOKUP = generative IQ · invent Wave BB without lab-book reopen · sell PEAK/bank-grounded as unlabeled open-chat · sell SAFE mean as IQ · sell span-fallback as true-continue · gold-substring PROMOTE · truncate-to-span as gen IQ · forever intent LOOKUP as success · over-refuse as win · NANOGEN11 = NANOGEN10+rename · bank stuffing BA-FOREVER · CTX/SMART/FAST/APP letter clones · rewrite AZ/AY/AX/… locks.
