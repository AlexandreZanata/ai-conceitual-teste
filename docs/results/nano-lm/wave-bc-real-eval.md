# BC-REAL-EVAL — product+ctx+speed + live battery (**DONE** — PROMOTE)

> Lab: `.local/pesquisa.md` §1 · §9 BC5 · Session: `.local/wave-bc/SESSION.md`  
> Parents: [formal-hopsfam-opsfam.md](formal-hopsfam-opsfam.md) · [formal-hfastlift-bc2.md](formal-hfastlift-bc2.md) · [formal-hctxlift2-ctxlift2.md](formal-hctxlift2-ctxlift2.md) · [formal-hnanogen13-nanogen13.md](formal-hnanogen13-nanogen13.md)  
> Module: `nano_lm/src/bc_real_eval_ops.py` · Runner: `npm run nano:bc:real-eval`

## Hypothesis

Final BC real eval: product+ctx+speed pass (OPSFAM·FASTLIFT·CTXLIFT2) + live ask battery (prod=eval; BC-FOREVER FP ABSTAIN; BA/BB forever hold; over-refuse LOOKUP) + generative claim only if BC4 H-NANOGEN13 PROMOTE (true_continue; real M1|M2|M3; span-fallback ≠ gen; never NANOGEN12+rename)

## Gate

| Pillar | Decision |
|--------|----------|
| BC1 H-OPSFAM | **PROMOTE (H-OPSFAM: BC-FOREVER FH 0; BA/BB hold 0; AZ hold 0; over-refuse 0; live FP 0; no bank stuffing)** |
| BC2 H-FASTLIFT | **PROMOTE (H-FASTLIFT: prod p50/p99 hold/lift; anti-FP hold; no live p99 regress vs BB-FASTHOLD baseline)** |
| BC3 H-CTXLIFT2 | **PROMOTE (H-CTXLIFT2: howto·cite·long content_ok; BC/BA/BB/AZ anti-FP hold; p50/p99 published; L_eff alone ≠ win)** |
| BC4 H-NANOGEN13 | **DEFER (H-NANOGEN13: stance=defer; CAPCHECK closed; no real M1|M2|M3; NANOGEN6·7 HOLD · NANOGEN8·9·10·11·12 DEFER stand; not NANOGEN12 rename)** (true_continue_mean=4.0) |
| Live ask battery | **PASS** (13/13) |
| Ship claim | `AF packaged stack + AQ product layer + AS trust path + ablated DECODE (snippet-prefix + gibberish-tail STRICT) — not unlabeled open chat LM · not TAC unlocked` |
| Decision | **PROMOTE** |

## Live ask battery

| ID | Kind | product_mode | expect | Row |
|----|------|--------------|--------|-----|
| BC-ASK-01 | known_lookup | **LOOKUP** | `LOOKUP` | PASS |
| BC-ASK-02 | ood_abstain | **ABSTAIN** | `ABSTAIN` | PASS |
| BC-ASK-03 | near_miss | **ABSTAIN** | `ABSTAIN` | PASS |
| BC-ASK-04 | labeled_peak | **PEAK** | `PEAK` | PASS |
| BC-ASK-05 | decode_content | **ABSTAIN** | `DECODE` | PASS |
| BC-ASK-06 | junk_trap | **ABSTAIN** | `ABSTAIN` | PASS |
| BC-ASK-07 | bc_forever_intent_fp | **ABSTAIN** | `ABSTAIN` | PASS |
| BC-ASK-08 | overrefuse_gold | **LOOKUP** | `LOOKUP` | PASS |
| BC-ASK-09 | az_hold_div | **ABSTAIN** | `ABSTAIN` | PASS |
| BC-ASK-10 | ba_forever_hold | **ABSTAIN** | `ABSTAIN` | PASS |
| BC-ASK-11 | bb_forever_hold | **ABSTAIN** | `ABSTAIN` | PASS |
| BC-ASK-12 | bc_forever_gcd_fp | **ABSTAIN** | `ABSTAIN` | PASS |
| BC-ASK-13 | bc_forever_shift_fp | **ABSTAIN** | `ABSTAIN` | PASS |

## Finding

1. Cite BC1–BC4 live summaries (no vanity rewrite of BB/BA/AZ locks).  
2. Live ask battery under max safe CPU (threads=12, workers=8, ~5.2s) — modes labeled; `wall_ms`/`n_new` mandatory; BC-FOREVER FP → ABSTAIN; over-refuse → LOOKUP; DECODE junk → ABSTAIN.  
3. Generative unlock **locked** because BC4 DEFER (no real M1|M2|M3; NANOGEN6·7 HOLD · NANOGEN8·9·10·11·12 DEFER stand).  
4. LOOKUP ≠ IQ · PEAK ≠ open-chat · SAFE ≠ quality · BA+BB PASS ≠ BC forever.  
5. Protocol: live_ask=True · eval_eq_prod=True · span_fallback_neq_gen=True.  

## Reproduce

```bash
npm run nano:bc:real-eval
npm run nano:nanogen13
npm run nano:bc:ctxlift2
npm run nano:bc:fastlift
npm run nano:opsfam
```

## Artifacts

- Summary: `results/nano-lm/wave-bc/bc_real_eval_summary.json`  
- Contract: `nano_lm/tests/test_bc_real_eval.py`

## Claims

| Allowed | Forbidden |
|---------|-----------|
| Product/ctx/speed PROMOTE + live battery | Unlabeled open chat |
| STRICT ship lock while BC4 DEFER | Gen unlock on DEFER/HOLD |
| Forever ABSTAIN · over-refuse LOOKUP | LOOKUP-as-IQ · invent BD |

SAFE note: SAFE / ADVSAFE false-hit score ≠ answer quality; SAFE = no wrong gold only (anti-FP); pack FH 0 ≠ forever held-out generalization; intent-mismatch LOOKUP = false-hit (floordiv/neg/gcd/lshift/rshift/nand); BA+BB forever PASS with BC-FOREVER FP = PACK THEATER; exact-gold ABSTAIN = product miss; gold-substring / gibberish-tail / span-fallback ≠ generative PROMOTE  
Anti-FP: LOOKUP|PEAK|DECODE|ABSTAIN labeled; never LOOKUP-as-IQ; never peak-as-open-chat; SAFE≠quality; gold-substring≠gen; intent-mismatch LOOKUP = false-hit (BC-FOREVER floordiv/neg/gcd/lshift/rshift/nand → add); exact-gold ABSTAIN = miss (a.clear()); BA-FOREVER pow·mod·max·sort·len FH must stay 0; BB-FOREVER min·xor·absdiff·and·or FH must stay 0; AZ hold div·sub·BIP FH must stay 0; BA+BB PASS with BC FP = PACK THEATER; truncate-to-span≠gen IQ; DECODE gibberish≠content_ok; eval path = prod ask path; generative bar = BC4 only under real new method; no NANOGEN13 = NANOGEN12+rename; no CTX/SMART/FAST clone; no invent Wave BD without lab-book reopen; prefer HOLD/defer over fake PROMOTE

Next: **BC6 BC-REPORT** — summary + paper-lab.
