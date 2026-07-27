# AU-REAL-EVAL — product + STRICT gen + live battery (**DONE** — PROMOTE)

> Lab: `.local/pesquisa.md` §5 AU4 · Session: `.local/wave-au/SESSION.md`  
> Parents: [formal-hprodhard-prodhard.md](formal-hprodhard-prodhard.md) · [formal-hshipreal-shipreal.md](formal-hshipreal-shipreal.md) · [formal-hnanogen5-nanogen5.md](formal-hnanogen5-nanogen5.md)  
> Module: `nano_lm/src/au_real_eval_ops.py` · Runner: `npm run nano:au:real-eval`

## Hypothesis

Final real eval: Caminho A product pass (PRODHARD+SHIPREAL) + live ask battery (prod=eval) + generative claim only if AU3 H-NANOGEN5 PROMOTE (strict_ablated≥5.5)

## Gate

| Pillar | Decision |
|--------|----------|
| AU1 H-PRODHARD | **PROMOTE (H-PRODHARD: live-audit debts closed)** |
| AU2 H-SHIPREAL | **PROMOTE (H-SHIPREAL: modes+content honest)** |
| AU3 H-NANOGEN5 | **PROMOTE** (strict 5.5) |
| Live ask battery | **PASS** (7/7) |
| Ship claim | `AF packaged stack + AQ product layer + AS trust path + ablated DECODE (snippet-prefix + gibberish-tail STRICT) — not unlabeled open chat LM` |
| Decision | **PROMOTE** |

## Live ask battery

| ID | Kind | product_mode | expect | Row |
|----|------|--------------|--------|-----|
| AU-ASK-01 | known_lookup | **LOOKUP** | `LOOKUP` | PASS |
| AU-ASK-02 | ood_abstain | **ABSTAIN** | `ABSTAIN` | PASS |
| AU-ASK-03 | near_miss | **ABSTAIN** | `ABSTAIN` | PASS |
| AU-ASK-04 | labeled_peak | **PEAK** | `PEAK` | PASS |
| AU-ASK-05 | decode_smoke | **DECODE** | `DECODE` | PASS |
| AU-ASK-06 | junk_trap | **ABSTAIN** | `ABSTAIN` | PASS |
| AU-ASK-07 | human_para | **LOOKUP** | `LOOKUP` | PASS |

## Finding

1. Cite AU1–AU3 live summaries (no vanity rewrite of AT locks).  
2. Live ask battery under max safe CPU (`cpus-2`) — modes labeled; `wall_ms`/`n_new` mandatory; answer usability scored; near-miss → ABSTAIN; human para → LOOKUP.  
3. Generative language allowed only because AU3 PROMOTE (STRICT ablated snippet-prefix + gibberish-tail) — still **not** unlabeled open chat.  
4. LOOKUP ≠ IQ · PEAK ≠ open-chat · SAFE ≠ quality · gold-substring ≠ gen.  
5. Protocol: live_ask=True · eval_eq_prod=True · gibberish_tail_fails=True.

## Reproduce

```bash
npm run nano:au:real-eval
npm run nano:nanogen5
npm run nano:shipreal
npm run nano:prodhard
```

## Artifacts

- Summary: `results/nano-lm/wave-au/real_eval_summary.json`  
- Contract: `nano_lm/tests/test_au_real_eval.py`

## Claims

| Allowed | Forbidden |
|---------|-----------|
| STRICT ablated DECODE after AU3 | Unlabeled open chat |
| Product PROMOTE + live battery 7/7 | LOOKUP-as-IQ · Wave AV invent |
| Mini-AGI-*inspired* stack shape (post AU4) | GPT-class / frontier chat |

Next: **AU5 AU-REPORT** — public summary + paper-lab.
