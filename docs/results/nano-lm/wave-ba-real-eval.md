# BA-REAL-EVAL — product+ctx+speed + live battery (**DONE** — PROMOTE)

> Lab: `.local/pesquisa.md` §1 · §8 BA5 · Session: `.local/wave-ba/SESSION.md`  
> Parents: [formal-hrealgain-realgain.md](formal-hrealgain-realgain.md) · [formal-hfastreal-ba2.md](formal-hfastreal-ba2.md) · [formal-hctxreal2-ctxreal2.md](formal-hctxreal2-ctxreal2.md) · [formal-hnanogen11-nanogen11.md](formal-hnanogen11-nanogen11.md)  
> Module: `nano_lm/src/ba_real_eval_ops.py` · Runner: `npm run nano:ba:real-eval`

## Hypothesis

Final BA real eval: product+ctx+speed pass (REALGAIN·FASTREAL·CTXREAL2) + live ask battery (prod=eval; forever FP ABSTAIN; over-refuse LOOKUP) + generative claim only if BA4 H-NANOGEN11 PROMOTE (true_continue; real M1|M2|M3; span-fallback ≠ gen; never NANOGEN10+rename)

## Gate

| Pillar | Decision |
|--------|----------|
| BA1 H-REALGAIN | **PROMOTE (H-REALGAIN: forever FH 0; AZ hold 0; over-refuse 0; live FP 0; no bank stuffing)** |
| BA2 H-FASTREAL | **PROMOTE (H-FASTREAL: prod p50/p99 published; anti-FP hold; no live p99 regress vs BA0 baseline)** |
| BA3 H-CTXREAL2 | **PROMOTE (H-CTXREAL2: howto·cite·long content_ok; anti-FP hold; p50/p99 published; L_eff alone ≠ win)** |
| BA4 H-NANOGEN11 | **DEFER (H-NANOGEN11: stance=defer; CAPCHECK closed; no real M1|M2|M3; NANOGEN6·7 HOLD · NANOGEN8·9·10 DEFER stand; not NANOGEN10 rename)** (true_continue_mean=4.0) |
| Live ask battery | **PASS** (10/10) |
| Ship claim | `AF packaged stack + AQ product layer + AS trust path + ablated DECODE (snippet-prefix + gibberish-tail STRICT) — not unlabeled open chat LM · not TAC unlocked` |
| Decision | **PROMOTE** |

## Live ask battery

| ID | Kind | product_mode | expect | Row |
|----|------|--------------|--------|-----|
| BA-ASK-01 | known_lookup | **LOOKUP** | `LOOKUP` | PASS |
| BA-ASK-02 | ood_abstain | **ABSTAIN** | `ABSTAIN` | PASS |
| BA-ASK-03 | near_miss | **ABSTAIN** | `ABSTAIN` | PASS |
| BA-ASK-04 | labeled_peak | **PEAK** | `PEAK` | PASS |
| BA-ASK-05 | decode_content | **ABSTAIN** | `DECODE` | PASS |
| BA-ASK-06 | junk_trap | **ABSTAIN** | `ABSTAIN` | PASS |
| BA-ASK-07 | forever_intent_fp | **ABSTAIN** | `ABSTAIN` | PASS |
| BA-ASK-08 | overrefuse_gold | **LOOKUP** | `LOOKUP` | PASS |
| BA-ASK-09 | az_hold_div | **ABSTAIN** | `ABSTAIN` | PASS |
| BA-ASK-10 | forever_list_fp | **ABSTAIN** | `ABSTAIN` | PASS |

## Finding

1. Cite BA1–BA4 live summaries (no vanity rewrite of AZ locks).  
2. Live ask battery under max safe CPU (threads=12, workers=10, ~5.1s) — modes labeled; `wall_ms`/`n_new` mandatory; forever FP → ABSTAIN; over-refuse → LOOKUP; DECODE junk → ABSTAIN.  
3. Generative unlock **locked** because BA4 DEFER (no real M1|M2|M3; NANOGEN6·7 HOLD · NANOGEN8·9·10 DEFER stand).  
4. LOOKUP ≠ IQ · PEAK ≠ open-chat · SAFE ≠ quality · pack PASS ≠ forever.  
5. Protocol: live_ask=True · eval_eq_prod=True · span_fallback_neq_gen=True.  

## Reproduce

```bash
npm run nano:ba:real-eval
npm run nano:nanogen11
npm run nano:ba:ctxreal2
npm run nano:ba:fastreal
npm run nano:realgain
```

## Artifacts

- Summary: `results/nano-lm/wave-ba/ba_real_eval_summary.json`  
- Contract: `nano_lm/tests/test_ba_real_eval.py`

## Claims

| Allowed | Forbidden |
|---------|-----------|
| Product/ctx/speed PROMOTE + live battery | Unlabeled open chat |
| STRICT ship lock while BA4 DEFER | Gen unlock on DEFER/HOLD |
| Forever ABSTAIN · over-refuse LOOKUP | LOOKUP-as-IQ · invent BB |

SAFE note: SAFE / ADVSAFE false-hit score ≠ answer quality; SAFE = no wrong gold only (anti-FP); pack FH 0 ≠ forever held-out generalization; intent-mismatch LOOKUP = false-hit (pow/mod/max/sort/len); exact-gold ABSTAIN = product miss; gold-substring / gibberish-tail / span-fallback ≠ generative PROMOTE  
Anti-FP: LOOKUP|PEAK|DECODE|ABSTAIN labeled; never LOOKUP-as-IQ; never peak-as-open-chat; SAFE≠quality; gold-substring≠gen; intent-mismatch LOOKUP = false-hit (BA-FOREVER pow/mod/max/sort/len); exact-gold ABSTAIN = miss (a.clear()); AZ hold div·sub·BIP FH must stay 0; truncate-to-span≠gen IQ; DECODE gibberish≠content_ok; eval path = prod ask path; pack PASS with forever FP = PACK THEATER; generative bar = BA4 only under real new method; no NANOGEN11 = NANOGEN10+rename; no CTX/SMART/FAST clone; no invent Wave BB without lab-book reopen; prefer HOLD/defer over fake PROMOTE

Next: **BA6 BA-REPORT** — summary + paper-lab.
