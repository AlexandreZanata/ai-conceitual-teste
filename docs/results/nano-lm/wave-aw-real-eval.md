# AW-REAL-EVAL — product keep + live battery (**DONE** — PROMOTE)

> Lab: `.local/pesquisa.md` §2 AW4 · Session: `.local/wave-aw/SESSION.md`  
> Parents: [formal-hprodkeep-prodkeep.md](formal-hprodkeep-prodkeep.md) · [formal-hshipkeep-shipkeep.md](formal-hshipkeep-shipkeep.md) · [formal-hnanogen7-nanogen7.md](formal-hnanogen7-nanogen7.md)  
> Module: `nano_lm/src/aw_real_eval_ops.py` · Runner: `npm run nano:aw:real-eval`

## Hypothesis

Final real eval: Caminho A product pass (PRODKEEP+SHIPKEEP) + live ask battery (prod=eval) + generative claim only if AW3 H-NANOGEN7 PROMOTE (TAC true_continue; span-fallback ≠ gen credit)

## Gate

| Pillar | Decision |
|--------|----------|
| AW1 H-PRODKEEP | **PROMOTE (H-PRODKEEP: Caminho A keep bars held under pressure)** |
| AW2 H-SHIPKEEP | **PROMOTE (H-SHIPKEEP: modes+content honest · DECODE law · keep after PRODKEEP)** |
| AW3 H-NANOGEN7 | **HOLD** (true_continue / gen_mean 4.0) |
| Live ask battery | **PASS** (8/8) |
| Ship claim | `AF packaged stack + AQ product layer + AS trust path + ablated DECODE (snippet-prefix + gibberish-tail STRICT) — not unlabeled open chat LM` |
| Decision | **PROMOTE** |

## Live ask battery

| ID | Kind | product_mode | expect | Row |
|----|------|--------------|--------|-----|
| AW-ASK-01 | known_lookup | **LOOKUP** | `LOOKUP` | PASS |
| AW-ASK-02 | ood_abstain | **ABSTAIN** | `ABSTAIN` | PASS |
| AW-ASK-03 | near_miss | **ABSTAIN** | `ABSTAIN` | PASS |
| AW-ASK-04 | labeled_peak | **PEAK** | `PEAK` | PASS |
| AW-ASK-05 | decode_content | **ABSTAIN** | `DECODE` | PASS |
| AW-ASK-06 | junk_trap | **ABSTAIN** | `ABSTAIN` | PASS |
| AW-ASK-07 | human_para | **LOOKUP** | `LOOKUP` | PASS |
| AW-ASK-08 | decode_gibberish_bar | **ABSTAIN** | `DECODE` | PASS |

## Finding

1. Cite AW1–AW3 live summaries (no vanity rewrite of AV/AU locks).  
2. Live ask battery under max safe CPU (`cpus-2`) — modes labeled; `wall_ms`/`n_new` mandatory; answer usability scored; near-miss → ABSTAIN; DECODE junk → ABSTAIN (content law); human para → LOOKUP.  
3. Generative / TAC true-continue unlock **locked** because AW3 HOLD (span-fallback ≠ gen IQ) — ship stays AV STRICT archive, **not** unlabeled open chat.  
4. LOOKUP ≠ IQ · PEAK ≠ open-chat · SAFE ≠ quality · gold-substring / truncate-to-span ≠ gen.  
5. Protocol: live_ask=True · eval_eq_prod=True · span_fallback_neq_gen=True.

## Reproduce

```bash
npm run nano:aw:real-eval
npm run nano:nanogen7
npm run nano:shipkeep
npm run nano:prodkeep
```

## Artifacts

- Summary: `results/nano-lm/wave-aw/real_eval_summary.json`  
- Contract: `nano_lm/tests/test_aw_real_eval.py`

## Claims

| Allowed | Forbidden |
|---------|-----------|
| Product PROMOTE + live battery 8/8 | Unlabeled open chat |
| AV STRICT ship lock while AW3 HOLD | TAC unlock on HOLD |
| DECODE usable or ABSTAIN | LOOKUP-as-IQ · Wave AX invent |

Next: **AW5 AW-REPORT** — public summary + paper-lab.
