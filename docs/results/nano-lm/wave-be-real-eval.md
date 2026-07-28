# BE-REAL-EVAL — product+util+ctx+speed + live battery (**DONE** — PROMOTE)

> Lab: `.local/pesquisa.md` §1 · §9 BE6 · Session: `.local/wave-be/SESSION.md`  
> Parents: [formal-hcompint-compint.md](formal-hcompint-compint.md) · [formal-hshipuse-shipuse.md](formal-hshipuse-shipuse.md) · [formal-hfastbe-fastbe.md](formal-hfastbe-fastbe.md) · [formal-hctxbe-ctxbe.md](formal-hctxbe-ctxbe.md) · [formal-hnanogen15-nanogen15.md](formal-hnanogen15-nanogen15.md)  
> Module: `nano_lm/src/be_real_eval_ops.py` · Runner: `npm run nano:be:real-eval`

## Hypothesis

Final BE real eval: product+util+ctx+speed pass (COMPINT·SHIPUSE·FASTBE·CTXBE) + live ask battery (prod=eval; BE-FOREVER FP ABSTAIN; BA…BD forever hold; over-refuse LOOKUP; utilization smoke) + generative claim only if BE5 H-NANOGEN15 PROMOTE (true_continue; real M1|M2|M3; span-fallback ≠ gen; never NANOGEN14+rename)

## Gate

| Pillar | Decision |
|--------|----------|
| BE1 H-COMPINT | **PROMOTE (H-COMPINT: BE-FOREVER FH 0; BA…BD hold 0; AZ hold 0; over-refuse 0; live FP 0; no bank stuffing)** |
| BE2 H-SHIPUSE | **PROMOTE (H-SHIPUSE: demo smoke · operator card · paper claim sync · BE residual ABSTAIN · Track A done)** |
| BE3 H-FASTBE | **PROMOTE (H-FASTBE: prod p50/p99 hold/lift; anti-FP hold; no live p99 regress vs H-FASTGAIN baseline)** |
| BE4 H-CTXBE | **PROMOTE (H-CTXBE: howto·cite·long content_ok; BD/BA/BB/BC/AZ anti-FP hold; p50/p99 published; L_eff alone ≠ win)** |
| BE5 H-NANOGEN15 | **DEFER (H-NANOGEN15: stance=defer; CAPCHECK closed; no real M1|M2|M3; DEFER once stop rule; NANOGEN6·7 HOLD · NANOGEN8…14 DEFER stand; not NANOGEN14 rename)** (true_continue_mean=4.0) |
| Live ask battery | **PASS** (15/15) |
| Ship claim | `AF packaged stack + AQ product layer + AS trust path + ablated DECODE (snippet-prefix + gibberish-tail STRICT) — not unlabeled open chat LM · not TAC unlocked` |
| Decision | **PROMOTE** |

## Live ask battery

| ID | Kind | product_mode | expect | Row |
|----|------|--------------|--------|-----|
| BE-ASK-01 | known_lookup | **LOOKUP** | `LOOKUP` | PASS |
| BE-ASK-02 | ood_abstain | **ABSTAIN** | `ABSTAIN` | PASS |
| BE-ASK-03 | near_miss | **ABSTAIN** | `ABSTAIN` | PASS |
| BE-ASK-04 | labeled_peak | **PEAK** | `PEAK` | PASS |
| BE-ASK-05 | decode_content | **ABSTAIN** | `DECODE` | PASS |
| BE-ASK-06 | junk_trap | **ABSTAIN** | `ABSTAIN` | PASS |
| BE-ASK-07 | be_forever_type_fp | **ABSTAIN** | `ABSTAIN` | PASS |
| BE-ASK-08 | overrefuse_gold | **LOOKUP** | `LOOKUP` | PASS |
| BE-ASK-09 | az_hold_div | **ABSTAIN** | `ABSTAIN` | PASS |
| BE-ASK-10 | ba_forever_hold | **ABSTAIN** | `ABSTAIN` | PASS |
| BE-ASK-11 | bb_forever_hold | **ABSTAIN** | `ABSTAIN` | PASS |
| BE-ASK-12 | bc_forever_hold | **ABSTAIN** | `ABSTAIN` | PASS |
| BE-ASK-13 | bd_forever_hold | **ABSTAIN** | `ABSTAIN` | PASS |
| BE-ASK-14 | be_forever_neighbor_fp | **ABSTAIN** | `ABSTAIN` | PASS |
| BE-ASK-15 | utilization_smoke | **LOOKUP** | `LOOKUP` | PASS |

## Finding

1. Cite BE1–BE5 live summaries (no vanity rewrite of BD/BC/BB/BA/AZ locks).  
2. Live ask battery under max safe CPU (threads=10, workers=6, ~5.3s · `cpus-6`) — modes labeled; `wall_ms`/`n_new` mandatory; BE-FOREVER FP → ABSTAIN; over-refuse → LOOKUP; DECODE junk → ABSTAIN.  
3. Generative unlock **locked** because BE5 DEFER (no real M1|M2|M3; DEFER once; NANOGEN6·7 HOLD · NANOGEN8…15 DEFER stand).  
4. LOOKUP ≠ IQ · PEAK ≠ open-chat · SAFE ≠ quality · BA…BD PASS ≠ BE forever.  
5. Protocol: live_ask=True · eval_eq_prod=True · utilization=True · span_fallback_neq_gen=True.  

## Reproduce

```bash
npm run nano:be:real-eval
npm run nano:nanogen15
npm run nano:ctxbe
npm run nano:fastbe
npm run nano:shipuse
npm run nano:compint
```

## Artifacts

- Summary: `results/nano-lm/wave-be/be_real_eval_summary.json`  
- Trials: `results/nano-lm/wave-be/real_eval_trials/`  
- Contract: `nano_lm/tests/test_be_real_eval.py`

## Claims

| Allowed | Forbidden |
|---------|-----------|
| AF packaged stack + AQ product layer + AS trust path + ablated DECODE (snippet-prefix + gibberish-tail STRICT) — not unlabeled open chat LM · not TAC unlocked | Open chat / mini-AGI while BE5 DEFER |
| Live battery PASS under anti-FP | Summary-only theater |
| Gen claim only if BE5 PROMOTE | NANOGEN15 = NANOGEN14+rename |

SAFE note: SAFE / ADVSAFE false-hit score ≠ answer quality; SAFE = no wrong gold only (anti-FP); pack FH 0 ≠ forever held-out generalization; type/coercion wrong-bank LOOKUP = false-hit (str→int→def add); BA…BD forever PASS with BE-FOREVER FP = PACK THEATER; exact-gold ABSTAIN = product miss; gold-substring / gibberish-tail / span-fallback ≠ generative PROMOTE  
Anti-FP: LOOKUP|PEAK|DECODE|ABSTAIN labeled; never LOOKUP-as-IQ; never peak-as-open-chat; SAFE≠quality; gold-substring≠gen; type/coercion LOOKUP = false-hit (BE-FOREVER str→int→add); exact-gold ABSTAIN = miss (a.clear()); BA-FOREVER pow·mod·max·sort·len FH must stay 0; BB-FOREVER min·xor·absdiff·and·or FH must stay 0; BC-FOREVER floordiv·neg·gcd·lshift·rshift·nand FH must stay 0; BD-FOREVER reverse≠f-string · mul≠add FH must stay 0; AZ hold div·sub·BIP FH must stay 0; BA…BD PASS with BE FP = PACK THEATER; truncate-to-span≠gen IQ; DECODE gibberish≠content_ok; eval path = prod ask path; generative bar = BE5 only under real new method; no NANOGEN15 = NANOGEN14+rename; no CTX/SMART/FAST clone; no invent Wave BF without lab-book reopen; prefer compositional gate over bank stuffing; prefer HOLD/defer over fake PROMOTE

Next: **BE7 BE-REPORT** (`npm run nano:be:report`).
