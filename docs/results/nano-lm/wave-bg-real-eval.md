# BG-REAL-EVAL — product+util+ctx+speed + live battery (**DONE** — PROMOTE)

> Lab: `.local/pesquisa.md` §1 · §9 BG6 · Session: `.local/wave-bg/SESSION.md`  
> Parents: [formal-hunaryint-unaryint.md](formal-hunaryint-unaryint.md) · [formal-hshippub-shippub.md](formal-hshippub-shippub.md) · [formal-hfastbg-fastbg.md](formal-hfastbg-fastbg.md) · [formal-hctxbg-ctxbg.md](formal-hctxbg-ctxbg.md) · [formal-hnanogen17-nanogen17.md](formal-hnanogen17-nanogen17.md)  
> Module: `nano_lm/src/bg_real_eval_ops.py` · Runner: `npm run nano:bg:real-eval`

## Hypothesis

Final BG real eval: product+util+ctx+speed pass (UNARYINT·SHIPPUB·FASTBG·CTXBG) + live ask battery (prod=eval; BG-FOREVER FP ABSTAIN; BA…BF forever hold; over-refuse LOOKUP; utilization smoke) + generative claim only if BG5 H-NANOGEN17 PROMOTE (true_continue; written M1|M2|M3 plan; span-fallback ≠ gen; never NANOGEN16+rename; else SKIP gen claim)

## Gate

| Pillar | Decision |
|--------|----------|
| BG1 H-UNARYINT | **PROMOTE (H-UNARYINT: BG-FOREVER FH 0; formal restore)** |
| BG2 H-SHIPPUB | **PROMOTE (H-SHIPPUB: Track A++ done; formal restore)** |
| BG3 H-FASTBG | **PROMOTE (H-FASTBG: p50/p99 hold; formal restore)** |
| BG4 H-CTXBG | **PROMOTE (H-CTXBG: howto·cite·long content_ok; BG/BF/BE/BD/BA/BB/BC/AZ anti-FP hold; p50/p99 published; L_eff alone ≠ win)** |
| BG5 H-NANOGEN17 | **SKIP (H-NANOGEN17: stance=skip; no written M1|M2|M3 plan; CAPCHECK closed; not empty DEFER letter; NANOGEN6·7 HOLD · NANOGEN8…15 DEFER · NANOGEN16 SKIP stand; not NANOGEN16 rename)** (true_continue_mean=0.0) |
| Live ask battery | **PASS** (17/17) |
| Ship claim | `AF packaged stack + AQ product layer + AS trust path + ablated DECODE (snippet-prefix + gibberish-tail STRICT) — not unlabeled open chat LM · not TAC unlocked` |
| Decision | **PROMOTE** |

## Live ask battery

| ID | Kind | product_mode | expect | Row |
|----|------|--------------|--------|-----|
| BG-ASK-01 | known_lookup | **LOOKUP** | `LOOKUP` | PASS |
| BG-ASK-02 | ood_abstain | **ABSTAIN** | `ABSTAIN` | PASS |
| BG-ASK-03 | near_miss | **ABSTAIN** | `ABSTAIN` | PASS |
| BG-ASK-04 | labeled_peak | **PEAK** | `PEAK` | PASS |
| BG-ASK-05 | decode_content | **ABSTAIN** | `DECODE` | PASS |
| BG-ASK-06 | junk_trap | **ABSTAIN** | `ABSTAIN` | PASS |
| BG-ASK-07 | bg_forever_unary_fp | **ABSTAIN** | `ABSTAIN` | PASS |
| BG-ASK-08 | overrefuse_gold | **LOOKUP** | `LOOKUP` | PASS |
| BG-ASK-09 | az_hold_div | **ABSTAIN** | `ABSTAIN` | PASS |
| BG-ASK-10 | ba_forever_hold | **ABSTAIN** | `ABSTAIN` | PASS |
| BG-ASK-11 | bb_forever_hold | **ABSTAIN** | `ABSTAIN` | PASS |
| BG-ASK-12 | bc_forever_hold | **ABSTAIN** | `ABSTAIN` | PASS |
| BG-ASK-13 | bd_forever_hold | **ABSTAIN** | `ABSTAIN` | PASS |
| BG-ASK-14 | be_forever_hold | **ABSTAIN** | `ABSTAIN` | PASS |
| BG-ASK-15 | bf_forever_hold | **ABSTAIN** | `ABSTAIN` | PASS |
| BG-ASK-16 | bg_forever_transform_fp | **ABSTAIN** | `ABSTAIN` | PASS |
| BG-ASK-17 | utilization_smoke | **LOOKUP** | `LOOKUP` | PASS |

## Finding

1. Cite BG1–BG5 live/formal summaries (no vanity rewrite of BF…AZ locks).  
2. Live ask battery under max safe CPU (threads=10, workers=6, ~5.2s · `cpus-6`) — modes labeled; `wall_ms`/`n_new` mandatory; BG-FOREVER FP → ABSTAIN; over-refuse → LOOKUP; DECODE junk → ABSTAIN.  
3. Generative unlock **locked** because BG5 SKIP (no written M1|M2|M3 plan; SKIP stop rule; NANOGEN6·7 HOLD · NANOGEN8…15 DEFER · NANOGEN16 SKIP · NANOGEN17 SKIP).  
4. LOOKUP ≠ IQ · PEAK ≠ open-chat · SAFE ≠ quality · BA…BF PASS ≠ BG forever.  
5. Protocol: live_ask=True · eval_eq_prod=True · utilization=True · span_fallback_neq_gen=True.  

## Reproduce

```bash
npm run nano:bg:real-eval
npm run nano:nanogen17
npm run nano:ctxbg
npm run nano:fastbg
npm run nano:shippub
npm run nano:unaryint
```

## Artifacts

- Summary: `results/nano-lm/wave-bg/bg_real_eval_summary.json`  
- Trials: `results/nano-lm/wave-bg/real_eval_trials/`  
- Contract: `nano_lm/tests/test_bg_real_eval.py`

## Claims

| Allowed | Forbidden |
|---------|-----------|
| AF packaged stack + AQ product layer + AS trust path + ablated DECODE (snippet-prefix + gibberish-tail STRICT) — not unlabeled open chat LM · not TAC unlocked | Open chat / mini-AGI while BG5 SKIP |
| Live battery PASS under anti-FP | Summary-only theater |
| Gen claim only if BG5 PROMOTE | NANOGEN17 = NANOGEN16+rename |

SAFE note: SAFE / ADVSAFE false-hit score ≠ answer quality; SAFE = no wrong gold only (anti-FP); pack FH 0 ≠ forever held-out generalization; unary/math/string-transform wrong-bank LOOKUP = false-hit (abs→def add · upper→f-string · all-truthy→clear); BA…BF forever PASS with BG-FOREVER FP = PACK THEATER; exact-gold ABSTAIN = product miss; gold-substring / gibberish-tail / span-fallback ≠ generative PROMOTE  
Anti-FP: LOOKUP|PEAK|DECODE|ABSTAIN labeled; never LOOKUP-as-IQ; never peak-as-open-chat; SAFE≠quality; gold-substring≠gen; unary/math LOOKUP = false-hit (BG-FOREVER abs/factorial→add); string-transform LOOKUP = false-hit (BG-FOREVER upper→f-string); aggregate/predicate LOOKUP = false-hit (all-truthy→clear); predicate/boolean LOOKUP = false-hit (BF-FOREVER even→add); type/coercion LOOKUP = false-hit (BE-FOREVER str→int→add); exact-gold ABSTAIN = miss (a.clear()); BA-FOREVER pow·mod·max·sort·len FH must stay 0; BB-FOREVER min·xor·absdiff·and·or FH must stay 0; BC-FOREVER floordiv·neg·gcd·lshift·rshift·nand FH must stay 0; BD-FOREVER reverse≠f-string · mul≠add FH must stay 0; BE-FOREVER str→int / type-coercion FH must stay 0; BF-FOREVER even/bool ≠ add FH must stay 0; AZ hold div·sub·BIP FH must stay 0; BA…BF PASS with BG FP = PACK THEATER; truncate-to-span≠gen IQ; DECODE gibberish≠content_ok; eval path = prod ask path; generative bar = BG5 only under written method plan; no NANOGEN17 without M1|M2|M3 plan; no CTX/SMART/FAST clone; no invent Wave BH without lab-book reopen; prefer unary/transform/arity gate over bank stuffing; prefer HOLD/SKIP over fake PROMOTE

Next: **BG7 BG-REPORT** (`npm run nano:bg:report`).
