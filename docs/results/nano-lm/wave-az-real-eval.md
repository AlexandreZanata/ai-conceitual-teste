# AZ-REAL-EVAL — product pass + live battery (**DONE** — PROMOTE)

> Lab: `.local/pesquisa.md` §5 AZ4 · Session: `.local/wave-az/SESSION.md`  
> Parents: [formal-hprodgen-prodgen.md](formal-hprodgen-prodgen.md) · [formal-hshipaz-shipaz.md](formal-hshipaz-shipaz.md) · [formal-hnanogen10-nanogen10.md](formal-hnanogen10-nanogen10.md)  
> Module: `nano_lm/src/az_real_eval_ops.py` · Runner: `npm run nano:az:real-eval`

## Hypothesis

Final real eval: Caminho A product pass (PRODGEN+SHIPAZ) + live ask battery (prod=eval; held-out FP ABSTAIN; over-refuse LOOKUP) + generative claim only if AZ3 H-NANOGEN10 PROMOTE (true_continue; real new method; span-fallback ≠ gen; never NANOGEN9+rename)

## Gate

| Pillar | Decision |
|--------|----------|
| AZ1 H-PRODGEN | **PROMOTE (H-PRODGEN: held-out FH 0; over-refuse 0; AY named + hard-natural hold; no bank stuffing)** |
| AZ2 H-SHIPAZ | **PROMOTE (H-SHIPAZ: modes+content honest · DECODE law · held-out ABSTAIN · over-refuse LOOKUP · named hold after PRODGEN)** |
| AZ3 H-NANOGEN10 | **DEFER (H-NANOGEN10: stance=defer; CAPCHECK closed; no real new method; NANOGEN6·7 HOLD · NANOGEN8·9 DEFER stand; not NANOGEN9 rename)** (true_continue_mean=4.0) |
| Live ask battery | **PASS** (9/9) |
| Ship claim | `AF packaged stack + AQ product layer + AS trust path + ablated DECODE (snippet-prefix + gibberish-tail STRICT) — not unlabeled open chat LM · not TAC unlocked` |
| Decision | **PROMOTE** |

## Live ask battery

| ID | Kind | product_mode | expect | Row |
|----|------|--------------|--------|-----|
| AZ-ASK-01 | known_lookup | **LOOKUP** | `LOOKUP` | PASS |
| AZ-ASK-02 | ood_abstain | **ABSTAIN** | `ABSTAIN` | PASS |
| AZ-ASK-03 | near_miss | **ABSTAIN** | `ABSTAIN` | PASS |
| AZ-ASK-04 | labeled_peak | **PEAK** | `PEAK` | PASS |
| AZ-ASK-05 | decode_content | **ABSTAIN** | `DECODE` | PASS |
| AZ-ASK-06 | junk_trap | **ABSTAIN** | `ABSTAIN` | PASS |
| AZ-ASK-07 | heldout_intent_fp | **ABSTAIN** | `ABSTAIN` | PASS |
| AZ-ASK-08 | overrefuse_gold | **LOOKUP** | `LOOKUP` | PASS |
| AZ-ASK-09 | ay_named_hold | **ABSTAIN** | `ABSTAIN` | PASS |

## Finding

1. Cite AZ1–AZ3 live summaries (no vanity rewrite of AY/AX locks).  
2. Live ask battery under max safe CPU (threads=14, workers=14, ~5.3s) — modes labeled; `wall_ms`/`n_new` mandatory; usability scored; near-miss → ABSTAIN; held-out FP → ABSTAIN; over-refuse → LOOKUP; DECODE junk → ABSTAIN.  
3. Generative unlock **locked** because AZ3 DEFER (no real new method; NANOGEN6·7 HOLD · NANOGEN8·9 DEFER stand; not NANOGEN9 rename) — ship stays STRICT archive, **not** unlabeled open chat.  
4. LOOKUP ≠ IQ · PEAK ≠ open-chat · SAFE ≠ quality · held-out intent LOOKUP = false-hit · exact-gold ABSTAIN = miss · gold-substring / span-fallback ≠ gen.  
5. Protocol: live_ask=True · eval_eq_prod=True · intent_fp=True · span_fallback_neq_gen=True.

## Reproduce

```bash
npm run nano:az:real-eval
npm run nano:nanogen10
npm run nano:shipaz
npm run nano:prodgen
```

## Artifacts

- Summary: `results/nano-lm/wave-az/real_eval_summary.json`  
- Contract: `nano_lm/tests/test_az_real_eval.py`

## Claims

| Allowed | Forbidden |
|---------|-----------|
| Product PROMOTE + live battery 9/9 | Unlabeled open chat |
| STRICT ship lock while AZ3 DEFER | Gen unlock on DEFER/HOLD |
| Held-out ABSTAIN · over-refuse LOOKUP | LOOKUP-as-IQ · invent BA |

Next: **AZ5 AZ-REPORT** — public summary + paper-lab.
