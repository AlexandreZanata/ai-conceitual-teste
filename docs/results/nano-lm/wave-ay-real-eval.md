# AY-REAL-EVAL — product pass + live battery (**DONE** — PROMOTE)

> Lab: `.local/pesquisa.md` §5 AY4 · Session: `.local/wave-ay/SESSION.md`  
> Parents: [formal-hprodint-prodint.md](formal-hprodint-prodint.md) · [formal-hshipay-shipay.md](formal-hshipay-shipay.md) · [formal-hnanogen9-nanogen9.md](formal-hnanogen9-nanogen9.md)  
> Module: `nano_lm/src/ay_real_eval_ops.py` · Runner: `npm run nano:ay:real-eval`

## Hypothesis

Final real eval: Caminho A product pass (PRODINT+SHIPAY) + live ask battery (prod=eval; intent-FP ABSTAIN) + generative claim only if AY3 H-NANOGEN9 PROMOTE (true_continue; real new method; span-fallback ≠ gen; never NANOGEN8+rename)

## Gate

| Pillar | Decision |
|--------|----------|
| AY1 H-PRODINT | **PROMOTE (H-PRODINT: intent FH 0 on live FP class; hard-natural hold; no bank stuffing)** |
| AY2 H-SHIPAY | **PROMOTE (H-SHIPAY: modes+content honest · DECODE law · hard-natural LOOKUP · intent-FP ABSTAIN after PRODINT)** |
| AY3 H-NANOGEN9 | **DEFER (H-NANOGEN9: stance=defer; CAPCHECK closed; no real new method; NANOGEN6·7 HOLD · NANOGEN8 DEFER stand; not NANOGEN8 rename)** (true_continue_mean=4.0) |
| Live ask battery | **PASS** (8/8) |
| Ship claim | `AF packaged stack + AQ product layer + AS trust path + ablated DECODE (snippet-prefix + gibberish-tail STRICT) — not unlabeled open chat LM · not TAC unlocked` |
| Decision | **PROMOTE** |

## Live ask battery

| ID | Kind | product_mode | expect | Row |
|----|------|--------------|--------|-----|
| AY-ASK-01 | known_lookup | **LOOKUP** | `LOOKUP` | PASS |
| AY-ASK-02 | ood_abstain | **ABSTAIN** | `ABSTAIN` | PASS |
| AY-ASK-03 | near_miss | **ABSTAIN** | `ABSTAIN` | PASS |
| AY-ASK-04 | labeled_peak | **PEAK** | `PEAK` | PASS |
| AY-ASK-05 | decode_content | **ABSTAIN** | `DECODE` | PASS |
| AY-ASK-06 | junk_trap | **ABSTAIN** | `ABSTAIN` | PASS |
| AY-ASK-07 | intent_fp | **ABSTAIN** | `ABSTAIN` | PASS |
| AY-ASK-08 | hard_natural_hold | **LOOKUP** | `LOOKUP` | PASS |

## Finding

1. Cite AY1–AY3 live summaries (no vanity rewrite of AX locks).  
2. Live ask battery under max safe CPU (threads=14, workers=14, ~5.3s) — modes labeled; `wall_ms`/`n_new` mandatory; usability scored; near-miss → ABSTAIN; intent-FP → ABSTAIN; DECODE junk → ABSTAIN; hard-natural → LOOKUP.  
3. Generative unlock **locked** because AY3 DEFER (no real new method; NANOGEN6·7 HOLD · NANOGEN8 DEFER stand; not NANOGEN8 rename) — ship stays STRICT archive, **not** unlabeled open chat.  
4. LOOKUP ≠ IQ · PEAK ≠ open-chat · SAFE ≠ quality · intent-mismatch LOOKUP = false-hit · gold-substring / span-fallback ≠ gen.  
5. Protocol: live_ask=True · eval_eq_prod=True · intent_fp=True · span_fallback_neq_gen=True.

## Reproduce

```bash
npm run nano:ay:real-eval
npm run nano:nanogen9
npm run nano:shipay
npm run nano:prodint
```

## Artifacts

- Summary: `results/nano-lm/wave-ay/real_eval_summary.json`  
- Contract: `nano_lm/tests/test_ay_real_eval.py`

## Claims

| Allowed | Forbidden |
|---------|-----------|
| Product PROMOTE + live battery 8/8 | Unlabeled open chat |
| STRICT ship lock while AY3 DEFER | Gen unlock on DEFER/HOLD |
| Intent-FP ABSTAIN · DECODE usable/ABSTAIN | LOOKUP-as-IQ · invent AZ |

Next: **AY5 AY-REPORT** — public summary + paper-lab.
