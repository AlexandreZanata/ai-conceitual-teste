# BD-REAL-EVAL — product+ctx+speed + live battery (**DONE** — PROMOTE)

> Lab: `.local/pesquisa.md` §1 · §9 BD5 · Session: `.local/wave-bd/SESSION.md`  
> Parents: [formal-hsemint-semint.md](formal-hsemint-semint.md) · [formal-hfastgain-fastgain.md](formal-hfastgain-fastgain.md) · [formal-hctxgain-ctxgain.md](formal-hctxgain-ctxgain.md) · [formal-hnanogen14-nanogen14.md](formal-hnanogen14-nanogen14.md)  
> Module: `nano_lm/src/bd_real_eval_ops.py` · Runner: `npm run nano:bd:real-eval`

## Hypothesis

Final BD real eval: product+ctx+speed pass (SEMINT·FASTGAIN·CTXGAIN) + live ask battery (prod=eval; BD-FOREVER FP ABSTAIN; BA/BB/BC forever hold; over-refuse LOOKUP) + generative claim only if BD4 H-NANOGEN14 PROMOTE (true_continue; real M1|M2|M3; span-fallback ≠ gen; never NANOGEN13+rename)

## Gate

| Pillar | Decision |
|--------|----------|
| BD1 H-SEMINT | **PROMOTE (H-SEMINT: BD-FOREVER FH 0; BA/BB/BC hold 0; AZ hold 0; over-refuse 0; live FP 0; no bank stuffing)** |
| BD2 H-FASTGAIN | **PROMOTE (H-FASTGAIN: prod p50/p99 hold/lift; anti-FP hold; no live p99 regress vs H-FASTLIFT baseline)** |
| BD3 H-CTXGAIN | **PROMOTE (H-CTXGAIN: howto·cite·long content_ok; BD/BA/BB/BC/AZ anti-FP hold; p50/p99 published; L_eff alone ≠ win)** |
| BD4 H-NANOGEN14 | **DEFER (H-NANOGEN14: stance=defer; CAPCHECK closed; no real M1|M2|M3; NANOGEN6·7 HOLD · NANOGEN8·9·10·11·12·13 DEFER stand; not NANOGEN13 rename)** (true_continue_mean=4.0) |
| Live ask battery | **PASS** (14/14) |
| Ship claim | `AF packaged stack + AQ product layer + AS trust path + ablated DECODE (snippet-prefix + gibberish-tail STRICT) — not unlabeled open chat LM · not TAC unlocked` |
| Decision | **PROMOTE** |

## Live ask battery

| ID | Kind | product_mode | expect | Row |
|----|------|--------------|--------|-----|
| BD-ASK-01 | known_lookup | **LOOKUP** | `LOOKUP` | PASS |
| BD-ASK-02 | ood_abstain | **ABSTAIN** | `ABSTAIN` | PASS |
| BD-ASK-03 | near_miss | **ABSTAIN** | `ABSTAIN` | PASS |
| BD-ASK-04 | labeled_peak | **PEAK** | `PEAK` | PASS |
| BD-ASK-05 | decode_content | **ABSTAIN** | `DECODE` | PASS |
| BD-ASK-06 | junk_trap | **ABSTAIN** | `ABSTAIN` | PASS |
| BD-ASK-07 | bd_forever_reverse_fp | **ABSTAIN** | `ABSTAIN` | PASS |
| BD-ASK-08 | overrefuse_gold | **LOOKUP** | `LOOKUP` | PASS |
| BD-ASK-09 | az_hold_div | **ABSTAIN** | `ABSTAIN` | PASS |
| BD-ASK-10 | ba_forever_hold | **ABSTAIN** | `ABSTAIN` | PASS |
| BD-ASK-11 | bb_forever_hold | **ABSTAIN** | `ABSTAIN` | PASS |
| BD-ASK-12 | bc_forever_hold | **ABSTAIN** | `ABSTAIN` | PASS |
| BD-ASK-13 | bd_forever_mul_fp | **ABSTAIN** | `ABSTAIN` | PASS |
| BD-ASK-14 | bd_forever_neighbor_fp | **ABSTAIN** | `ABSTAIN` | PASS |

## Finding

1. Cite BD1–BD4 live summaries (no vanity rewrite of BC/BB/BA/AZ locks).  
2. Live ask battery under max safe CPU (threads=12, workers=8, ~3.5s) — modes labeled; `wall_ms`/`n_new` mandatory; BD-FOREVER FP → ABSTAIN; over-refuse → LOOKUP; DECODE junk → ABSTAIN.  
3. Generative unlock **locked** because BD4 DEFER (no real M1|M2|M3; NANOGEN6·7 HOLD · NANOGEN8·9·10·11·12·13 DEFER stand).  
4. LOOKUP ≠ IQ · PEAK ≠ open-chat · SAFE ≠ quality · BA+BB+BC PASS ≠ BD forever.  
5. Protocol: live_ask=True · eval_eq_prod=True · span_fallback_neq_gen=True.  

## Reproduce

```bash
npm run nano:bd:real-eval
npm run nano:nanogen14
npm run nano:bd:ctxgain
npm run nano:bd:fastgain
npm run nano:semint
```

## Artifacts

- Summary: `results/nano-lm/wave-bd/bd_real_eval_summary.json`  
- Trials: `results/nano-lm/wave-bd/real_eval_trials/`  
- Contract: `nano_lm/tests/test_bd_real_eval.py`

## Claims

| Allowed | Forbidden |
|---------|-----------|
| AF packaged stack + AQ product layer + AS trust path + ablated DECODE (snippet-prefix + gibberish-tail STRICT) — not unlabeled open chat LM · not TAC unlocked | Open chat / mini-AGI while BD4 DEFER |
| Live battery PASS under anti-FP | Summary-only theater |
| Gen claim only if BD4 PROMOTE | NANOGEN14 = NANOGEN13+rename |

SAFE note: SAFE / ADVSAFE false-hit score ≠ answer quality; SAFE = no wrong gold only (anti-FP); pack FH 0 ≠ forever held-out generalization; semantic wrong-bank LOOKUP = false-hit (reverse→f-string · mul→add); BA+BB+BC forever PASS with BD-FOREVER FP = PACK THEATER; exact-gold ABSTAIN = product miss; gold-substring / gibberish-tail / span-fallback ≠ generative PROMOTE  
Anti-FP: LOOKUP|PEAK|DECODE|ABSTAIN labeled; never LOOKUP-as-IQ; never peak-as-open-chat; SAFE≠quality; gold-substring≠gen; semantic wrong-bank LOOKUP = false-hit (BD-FOREVER reverse→f-string / mul→add); exact-gold ABSTAIN = miss (a.clear()); BA-FOREVER pow·mod·max·sort·len FH must stay 0; BB-FOREVER min·xor·absdiff·and·or FH must stay 0; BC-FOREVER floordiv·neg·gcd·lshift·rshift·nand FH must stay 0; AZ hold div·sub·BIP FH must stay 0; BA+BB+BC PASS with BD FP = PACK THEATER; truncate-to-span≠gen IQ; DECODE gibberish≠content_ok; eval path = prod ask path; generative bar = BD4 only under real new method; no NANOGEN14 = NANOGEN13+rename; no CTX/SMART/FAST clone; no invent Wave BE without lab-book reopen; prefer HOLD/defer over fake PROMOTE

Next: **BD7 BD-FREEZE** (`npm run nano:bd:freeze`) — BD6 BD-REPORT **PROMOTE**.
