# AT-REAL-EVAL — product + gen + live battery (**DONE** — PROMOTE)

> Lab: `.local/pesquisa.md` §5 AT4 · Session: `.local/wave-at/SESSION.md`  
> Parents: [formal-hprodreg-prodreg.md](formal-hprodreg-prodreg.md) · [formal-hshipapp-shipapp.md](formal-hshipapp-shipapp.md) · [formal-hnanogen4-nanogen4.md](formal-hnanogen4-nanogen4.md)  
> Module: `nano_lm/src/real_eval_ops.py` · Runner: `npm run nano:at:real-eval`

## Hypothesis

Final real eval: Caminho A product pass + live ask battery + generative claim only if AT3 H-NANOGEN4 PROMOTE (ablated≥5.0)

## Gate

| Pillar | Decision |
|--------|----------|
| AT1 H-PRODREG | **PROMOTE (H-PRODREG: all Caminho A bars hold)** |
| AT2 H-SHIPAPP | **PROMOTE** |
| AT3 H-NANOGEN4 | **PROMOTE** (ablated 5.5) |
| Live ask battery | **PASS** (6/6) |
| Ship claim | `AF packaged stack + AQ product layer + AS trust path + ablated DECODE (snippet-prefix) — not unlabeled open chat LM` |
| Decision | **PROMOTE** |

## Live ask battery

| ID | Kind | product_mode | expect | Row |
|----|------|--------------|--------|-----|
| AT-ASK-01 | known_lookup | **LOOKUP** | `LOOKUP` | PASS |
| AT-ASK-02 | ood_abstain | **ABSTAIN** | `ABSTAIN` | PASS |
| AT-ASK-03 | near_miss | **ABSTAIN** | `ABSTAIN` | PASS |
| AT-ASK-04 | labeled_peak | **PEAK** | `PEAK` | PASS |
| AT-ASK-05 | decode_smoke | **DECODE** | `DECODE` | PASS |
| AT-ASK-06 | junk_trap | **ABSTAIN** | `ABSTAIN` | PASS |

## Finding

1. Cite AT1–AT3 live summaries (no vanity rewrite of AS locks).  
2. Live ask battery under max safe CPU (`cpus-2`) — modes labeled; `wall_ms`/`n_new` mandatory; near-miss SegWit/BIP-39 domain confusion → ABSTAIN refuse (anti-FP).  
3. Generative language allowed only because AT3 PROMOTE (ablated snippet-prefix DECODE) — still **not** unlabeled open chat.  
4. LOOKUP ≠ IQ · PEAK ≠ open-chat · SAFE ≠ quality.  
5. Protocol: live_ask=True · summary_only_forbidden=True.

## Reproduce

```bash
npm run nano:at:real-eval
npm run nano:nanogen4
npm run nano:shipapp
```

## Artifacts

- Summary: `results/nano-lm/wave-at/real_eval_summary.json`  
- Contract: `nano_lm/tests/test_real_eval.py`

## Claims

| Allowed | Forbidden |
|---------|-----------|
| Ablated DECODE (snippet-prefix) after AT3 | Unlabeled open chat |
| Product PROMOTE + live battery | LOOKUP-as-IQ · Wave AU invent |
| Mini-AGI-*inspired* stack shape (post AT4) | GPT-class / frontier chat |

Next: **AT5 AT-REPORT** — **DONE PROMOTE** → [wave-at-summary.md](wave-at-summary.md). **AT6 AT-FREEZE** — next.
