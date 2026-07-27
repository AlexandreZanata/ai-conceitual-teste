# AV-REAL-EVAL — product + live battery (**DONE** — PROMOTE)

> Lab: `.local/pesquisa.md` §5 AV4 · Session: `.local/wave-av/SESSION.md`  
> Parents: [formal-hprodship-prodship.md](formal-hprodship-prodship.md) · [formal-hshipui2-shipui2.md](formal-hshipui2-shipui2.md) · [formal-hnanogen6-nanogen6.md](formal-hnanogen6-nanogen6.md)  
> Module: `nano_lm/src/av_real_eval_ops.py` · Runner: `npm run nano:av:real-eval`

## Hypothesis

Final real eval: Caminho A product pass (PRODSHIP+SHIPUI2) + live ask battery (prod=eval) + generative claim only if AV3 H-NANOGEN6 PROMOTE (true_continue; span-fallback ≠ gen credit)

## Gate

| Pillar | Decision |
|--------|----------|
| AV1 H-PRODSHIP | **PROMOTE (H-PRODSHIP: Caminho A ship bars closed)** |
| AV2 H-SHIPUI2 | **PROMOTE (H-SHIPUI2: modes+content honest · DECODE law)** |
| AV3 H-NANOGEN6 | **HOLD** (true_continue mean 4.0) |
| Live ask battery | **PASS** (8/8) |
| Ship claim | `AF packaged stack + AQ product layer + AS trust path + ablated DECODE (snippet-prefix + gibberish-tail STRICT) — not unlabeled open chat LM` |
| Decision | **PROMOTE** |

## Live ask battery

| ID | Kind | product_mode | expect | Row |
|----|------|--------------|--------|-----|
| AV-ASK-01 | known_lookup | **LOOKUP** | `LOOKUP` | PASS |
| AV-ASK-02 | ood_abstain | **ABSTAIN** | `ABSTAIN` | PASS |
| AV-ASK-03 | near_miss | **ABSTAIN** | `ABSTAIN` | PASS |
| AV-ASK-04 | labeled_peak | **PEAK** | `PEAK` | PASS |
| AV-ASK-05 | decode_content | **ABSTAIN** | `DECODE` | PASS |
| AV-ASK-06 | junk_trap | **ABSTAIN** | `ABSTAIN` | PASS |
| AV-ASK-07 | human_para | **LOOKUP** | `LOOKUP` | PASS |
| AV-ASK-08 | decode_gibberish_bar | **ABSTAIN** | `DECODE` | PASS |

## Finding

1. Cite AV1–AV3 live summaries (no vanity rewrite of AU locks).  
2. Live ask battery under max safe CPU (`cpus-2`) — modes labeled; `wall_ms`/`n_new` mandatory; answer usability scored; near-miss → ABSTAIN; DECODE junk → ABSTAIN (content law); human para → LOOKUP.  
3. Generative / true-continue unlock **locked** because AV3 HOLD (span-fallback ≠ gen IQ) — ship stays AU STRICT archive, **not** unlabeled open chat.  
4. LOOKUP ≠ IQ · PEAK ≠ open-chat · SAFE ≠ quality · gold-substring / truncate-to-span ≠ gen.  
5. Protocol: live_ask=True · eval_eq_prod=True · span_fallback_neq_gen=True.

## Reproduce

```bash
npm run nano:av:real-eval
npm run nano:nanogen6
npm run nano:shipui2
npm run nano:prodship
```

## Artifacts

- Summary: `results/nano-lm/wave-av/real_eval_summary.json`  
- Contract: `nano_lm/tests/test_av_real_eval.py`

## Claims

| Allowed | Forbidden |
|---------|-----------|
| Product PROMOTE + live battery 8/8 | Unlabeled open chat |
| AU STRICT ship lock while AV3 HOLD | true-continue unlock on HOLD |
| DECODE usable or ABSTAIN | LOOKUP-as-IQ · Wave AW invent |

Next: **AV5 AV-REPORT** — public summary + paper-lab.
