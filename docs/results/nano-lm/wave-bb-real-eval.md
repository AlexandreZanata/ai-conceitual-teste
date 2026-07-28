# BB-REAL-EVAL — product+ctx+speed + live battery (**DONE** — PROMOTE)

> Lab: `.local/pesquisa.md` §1 · §8 BB5 · Session: `.local/wave-bb/SESSION.md`  
> Parents: [formal-hintentgen-intentgen.md](formal-hintentgen-intentgen.md) · [formal-hfasthold-fasthold.md](formal-hfasthold-fasthold.md) · [formal-hctxhold-ctxhold.md](formal-hctxhold-ctxhold.md) · [formal-hnanogen12-nanogen12.md](formal-hnanogen12-nanogen12.md)  
> Module: `nano_lm/src/bb_real_eval_ops.py` · Runner: `npm run nano:bb:real-eval`

## Hypothesis

Final BB real eval: product+ctx+speed pass (INTENTGEN·FASTHOLD·CTXHOLD) + live ask battery (prod=eval; BB-FOREVER FP ABSTAIN; BA forever hold; over-refuse LOOKUP) + generative claim only if BB4 H-NANOGEN12 PROMOTE (true_continue; real M1|M2|M3; span-fallback ≠ gen; never NANOGEN11+rename)

## Gate

| Pillar | Decision |
|--------|----------|
| BB1 H-INTENTGEN | **PROMOTE (H-INTENTGEN: BB-FOREVER FH 0; BA hold 0; AZ hold 0; over-refuse 0; live FP 0; no bank stuffing)** |
| BB2 H-FASTHOLD | **PROMOTE (H-FASTHOLD: prod p50/p99 hold; anti-FP hold; no live p99 regress vs BA-FASTREAL baseline)** |
| BB3 H-CTXHOLD | **PROMOTE (H-CTXHOLD: howto·cite·long content_ok; BB/BA/AZ anti-FP hold; p50/p99 published; L_eff alone ≠ win)** |
| BB4 H-NANOGEN12 | **DEFER (H-NANOGEN12: stance=defer; CAPCHECK closed; no real M1|M2|M3; NANOGEN6·7 HOLD · NANOGEN8·9·10·11 DEFER stand; not NANOGEN11 rename)** (true_continue_mean=4.0) |
| Live ask battery | **PASS** (12/12) |
| Ship claim | `AF packaged stack + AQ product layer + AS trust path + ablated DECODE (snippet-prefix + gibberish-tail STRICT) — not unlabeled open chat LM · not TAC unlocked` |
| Decision | **PROMOTE** |

## Live ask battery

| ID | Kind | product_mode | expect | Row |
|----|------|--------------|--------|-----|
| BB-ASK-01 | known_lookup | **LOOKUP** | `LOOKUP` | PASS |
| BB-ASK-02 | ood_abstain | **ABSTAIN** | `ABSTAIN` | PASS |
| BB-ASK-03 | near_miss | **ABSTAIN** | `ABSTAIN` | PASS |
| BB-ASK-04 | labeled_peak | **PEAK** | `PEAK` | PASS |
| BB-ASK-05 | decode_content | **ABSTAIN** | `DECODE` | PASS |
| BB-ASK-06 | junk_trap | **ABSTAIN** | `ABSTAIN` | PASS |
| BB-ASK-07 | bb_forever_intent_fp | **ABSTAIN** | `ABSTAIN` | PASS |
| BB-ASK-08 | overrefuse_gold | **LOOKUP** | `LOOKUP` | PASS |
| BB-ASK-09 | az_hold_div | **ABSTAIN** | `ABSTAIN` | PASS |
| BB-ASK-10 | ba_forever_hold | **ABSTAIN** | `ABSTAIN` | PASS |
| BB-ASK-11 | bb_forever_xor_fp | **ABSTAIN** | `ABSTAIN` | PASS |
| BB-ASK-12 | bb_forever_absdiff_fp | **ABSTAIN** | `ABSTAIN` | PASS |

## Finding

1. Cite BB1–BB4 live summaries (no vanity rewrite of BA/AZ locks).  
2. Live ask battery under max safe CPU (threads=10, workers=6, ~5.3s) — modes labeled; `wall_ms`/`n_new` mandatory; BB-FOREVER FP → ABSTAIN; over-refuse → LOOKUP; DECODE junk → ABSTAIN.  
3. Generative unlock **locked** because BB4 DEFER (no real M1|M2|M3; NANOGEN6·7 HOLD · NANOGEN8·9·10·11 DEFER stand).  
4. LOOKUP ≠ IQ · PEAK ≠ open-chat · SAFE ≠ quality · pack PASS ≠ forever · BA PASS ≠ BB forever.  
5. Protocol: live_ask=True · eval_eq_prod=True · span_fallback_neq_gen=True.  

## Reproduce

```bash
npm run nano:bb:real-eval
npm run nano:nanogen12
npm run nano:bb:ctxhold
npm run nano:bb:fasthold
npm run nano:intentgen
```

## Artifacts

- Summary: `results/nano-lm/wave-bb/bb_real_eval_summary.json`  
- Contract: `nano_lm/tests/test_bb_real_eval.py`

## Claims

| Allowed | Forbidden |
|---------|-----------|
| Product/ctx/speed PROMOTE + live battery | Unlabeled open chat |
| STRICT ship lock while BB4 DEFER | Gen unlock on DEFER/HOLD |
| Forever ABSTAIN · over-refuse LOOKUP | LOOKUP-as-IQ · invent BC |

SAFE note: SAFE / ADVSAFE false-hit score ≠ answer quality; SAFE = no wrong gold only (anti-FP); pack FH 0 ≠ forever held-out generalization; intent-mismatch LOOKUP = false-hit (min/xor/absdiff/and/or); BA-FOREVER PASS with BB-FOREVER FP = PACK THEATER; exact-gold ABSTAIN = product miss; gold-substring / gibberish-tail / span-fallback ≠ generative PROMOTE  
Anti-FP: LOOKUP|PEAK|DECODE|ABSTAIN labeled; never LOOKUP-as-IQ; never peak-as-open-chat; SAFE≠quality; gold-substring≠gen; intent-mismatch LOOKUP = false-hit (BB-FOREVER min/xor/absdiff/and/or → add); exact-gold ABSTAIN = miss (a.clear()); BA-FOREVER pow·mod·max·sort·len FH must stay 0; AZ hold div·sub·BIP FH must stay 0; BA PASS with BB FP = PACK THEATER; truncate-to-span≠gen IQ; DECODE gibberish≠content_ok; eval path = prod ask path; generative bar = BB4 only under real new method; no NANOGEN12 = NANOGEN11+rename; no CTX/SMART/FAST clone; no invent Wave BC without lab-book reopen; prefer HOLD/defer over fake PROMOTE

Next: **BB6 BB-REPORT** — summary + paper-lab.
