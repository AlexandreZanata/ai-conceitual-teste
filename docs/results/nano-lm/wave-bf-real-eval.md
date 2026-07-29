# BF-REAL-EVAL — product+util+ctx+speed + live battery (**DONE** — PROMOTE)

> Lab: `.local/pesquisa.md` §1 · §9 BF6 · Session: `.local/wave-bf/SESSION.md`  
> Parents: [formal-hpredint-predint.md](formal-hpredint-predint.md) · [formal-hshipuse2-shipuse2.md](formal-hshipuse2-shipuse2.md) · [formal-hfastbf-fastbf.md](formal-hfastbf-fastbf.md) · [formal-hctxbf-ctxbf.md](formal-hctxbf-ctxbf.md) · [formal-hnanogen16-nanogen16.md](formal-hnanogen16-nanogen16.md)  
> Module: `nano_lm/src/bf_real_eval_ops.py` · Runner: `npm run nano:bf:real-eval`

## Hypothesis

Final BF real eval: product+util+ctx+speed pass (PREDINT·SHIPUSE2·FASTBF·CTXBF) + live ask battery (prod=eval; BF-FOREVER FP ABSTAIN; BA…BE forever hold; over-refuse LOOKUP; utilization smoke) + generative claim only if BF5 H-NANOGEN16 PROMOTE (true_continue; written M1|M2|M3 plan; span-fallback ≠ gen; never NANOGEN15+rename; else SKIP gen claim)

## Gate

| Pillar | Decision |
|--------|----------|
| BF1 H-PREDINT | **PROMOTE (H-PREDINT: BF-FOREVER FH 0; BA…BE hold 0; AZ hold 0; over-refuse 0; live FP 0; no bank stuffing)** |
| BF2 H-SHIPUSE2 | **PROMOTE (H-SHIPUSE2: Track A+ deepen · H-SHIPUSE hold · BF residual ABSTAIN · operator · paper sync)** |
| BF3 H-FASTBF | **PROMOTE (H-FASTBF: prod p50/p99 hold/lift; anti-FP hold; no live p99 regress vs H-FASTBE baseline)** |
| BF4 H-CTXBF | **PROMOTE (H-CTXBF: howto·cite·long content_ok; BF/BE/BD/BA/BB/BC/AZ anti-FP hold; p50/p99 published; L_eff alone ≠ win)** |
| BF5 H-NANOGEN16 | **SKIP (H-NANOGEN16: stance=skip; no written M1|M2|M3 plan; CAPCHECK closed; not empty DEFER letter; NANOGEN6·7 HOLD · NANOGEN8…15 DEFER stand; not NANOGEN15 rename)** (true_continue_mean=4.0) |
| Live ask battery | **PASS** (16/16) |
| Ship claim | `AF packaged stack + AQ product layer + AS trust path + ablated DECODE (snippet-prefix + gibberish-tail STRICT) — not unlabeled open chat LM · not TAC unlocked` |
| Decision | **PROMOTE** |

## Live ask battery

| ID | Kind | product_mode | expect | Row |
|----|------|--------------|--------|-----|
| BF-ASK-01 | known_lookup | **LOOKUP** | `LOOKUP` | PASS |
| BF-ASK-02 | ood_abstain | **ABSTAIN** | `ABSTAIN` | PASS |
| BF-ASK-03 | near_miss | **ABSTAIN** | `ABSTAIN` | PASS |
| BF-ASK-04 | labeled_peak | **PEAK** | `PEAK` | PASS |
| BF-ASK-05 | decode_content | **ABSTAIN** | `DECODE` | PASS |
| BF-ASK-06 | junk_trap | **ABSTAIN** | `ABSTAIN` | PASS |
| BF-ASK-07 | bf_forever_predicate_fp | **ABSTAIN** | `ABSTAIN` | PASS |
| BF-ASK-08 | overrefuse_gold | **LOOKUP** | `LOOKUP` | PASS |
| BF-ASK-09 | az_hold_div | **ABSTAIN** | `ABSTAIN` | PASS |
| BF-ASK-10 | ba_forever_hold | **ABSTAIN** | `ABSTAIN` | PASS |
| BF-ASK-11 | bb_forever_hold | **ABSTAIN** | `ABSTAIN` | PASS |
| BF-ASK-12 | bc_forever_hold | **ABSTAIN** | `ABSTAIN` | PASS |
| BF-ASK-13 | bd_forever_hold | **ABSTAIN** | `ABSTAIN` | PASS |
| BF-ASK-14 | be_forever_hold | **ABSTAIN** | `ABSTAIN` | PASS |
| BF-ASK-15 | bf_forever_neighbor_fp | **ABSTAIN** | `ABSTAIN` | PASS |
| BF-ASK-16 | utilization_smoke | **LOOKUP** | `LOOKUP` | PASS |

## Finding

1. Cite BF1–BF5 live summaries (no vanity rewrite of BE/BD/BC/BB/BA/AZ locks).  
2. Live ask battery under max safe CPU (threads=10, workers=6, ~5.1s · `cpus-6`) — modes labeled; `wall_ms`/`n_new` mandatory; BF-FOREVER FP → ABSTAIN; over-refuse → LOOKUP; DECODE junk → ABSTAIN.  
3. Generative unlock **locked** because BF5 SKIP (no written M1|M2|M3 plan; SKIP stop rule; NANOGEN6·7 HOLD · NANOGEN8…15 DEFER · NANOGEN16 SKIP).  
4. LOOKUP ≠ IQ · PEAK ≠ open-chat · SAFE ≠ quality · BA…BE PASS ≠ BF forever.  
5. Protocol: live_ask=True · eval_eq_prod=True · utilization=True · span_fallback_neq_gen=True.  

## Reproduce

```bash
npm run nano:bf:real-eval
npm run nano:nanogen16
npm run nano:ctxbf
npm run nano:fastbf
npm run nano:shipuse2
npm run nano:predint
```

## Artifacts

- Summary: `results/nano-lm/wave-bf/bf_real_eval_summary.json`  
- Trials: `results/nano-lm/wave-bf/real_eval_trials/`  
- Contract: `nano_lm/tests/test_bf_real_eval.py`

## Claims

| Allowed | Forbidden |
|---------|-----------|
| AF packaged stack + AQ product layer + AS trust path + ablated DECODE (snippet-prefix + gibberish-tail STRICT) — not unlabeled open chat LM · not TAC unlocked | Open chat / mini-AGI while BF5 SKIP |
| Live battery PASS under anti-FP | Summary-only theater |
| Gen claim only if BF5 PROMOTE | NANOGEN16 = NANOGEN15+rename |

SAFE note: SAFE / ADVSAFE false-hit score ≠ answer quality; SAFE = no wrong gold only (anti-FP); pack FH 0 ≠ forever held-out generalization; predicate/boolean wrong-bank LOOKUP = false-hit (even→def add); BA…BE forever PASS with BF-FOREVER FP = PACK THEATER; exact-gold ABSTAIN = product miss; gold-substring / gibberish-tail / span-fallback ≠ generative PROMOTE  
Anti-FP: LOOKUP|PEAK|DECODE|ABSTAIN labeled; never LOOKUP-as-IQ; never peak-as-open-chat; SAFE≠quality; gold-substring≠gen; predicate/boolean LOOKUP = false-hit (BF-FOREVER even→add); type/coercion LOOKUP = false-hit (BE-FOREVER str→int→add); exact-gold ABSTAIN = miss (a.clear()); BA-FOREVER pow·mod·max·sort·len FH must stay 0; BB-FOREVER min·xor·absdiff·and·or FH must stay 0; BC-FOREVER floordiv·neg·gcd·lshift·rshift·nand FH must stay 0; BD-FOREVER reverse≠f-string · mul≠add FH must stay 0; BE-FOREVER str→int / type-coercion FH must stay 0; AZ hold div·sub·BIP FH must stay 0; BA…BE PASS with BF FP = PACK THEATER; truncate-to-span≠gen IQ; DECODE gibberish≠content_ok; eval path = prod ask path; generative bar = BF5 only under written method plan; no NANOGEN16 without M1|M2|M3 plan; no CTX/SMART/FAST clone; no invent Wave BG without lab-book reopen; prefer predicate/schema gate over bank stuffing; prefer HOLD/SKIP over fake PROMOTE

Next: **BF7 BF-REPORT** (`npm run nano:bf:report`).
