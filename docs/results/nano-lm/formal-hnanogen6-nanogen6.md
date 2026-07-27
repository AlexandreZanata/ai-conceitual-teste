# H-NANOGEN6 — true continue / refuse-or-continue (**DONE** — HOLD)

> Lab: `.local/pesquisa.md` §5 AV3 · Session: `.local/wave-av/SESSION.md`  
> Parent: [formal-hnanogen5-nanogen5.md](formal-hnanogen5-nanogen5.md) (STRICT archive **5.5**) · Pack: same NANOGEN held-out+para · true-gen judge  
> Module: `nano_lm/src/nanogen6_ops.py` · Runner: `npm run nano:nanogen6`

## Hypothesis

One idea: refuse-or-continue DECODE with fallback labeling — score only novel readable continue tokens; truncate-to-retrieved-span must label PEAK/LOOKUP fallback (zero gen credit); gibberish → ABSTAIN; wall_ms/n_new ≠ content_ok; not a NANOGEN5 5.5 truncate-bar clone; bar = true_continue_ablated PROMOTE else HOLD

## Gate

| Metric | Result | Pass bar |
|--------|-------:|----------|
| LOOKUP mean | **9.0** | ≥ 7.0 |
| true_continue ablated mean | **4.0** | ≥ **5.5** for PROMOTE |
| vs H-NANOGEN5 STRICT archive | **5.5** | span-fallback ≠ gen credit |
| GENERATE peak_on mean | **4.0** | compare only |
| bank-grounded mean | **4.0** | compare only (anti-FP) |
| n_true_continue | **0** | novel continue count |
| n_span_fallback | **3** | PEAK/LOOKUP fallback (0 gen IQ) |
| n_snippet_prefix | **10** | ablated seed count |
| peak_only_lift / span_only | **True** | no true_continue → HOLD |
| n_abstain / n_bank_grounded | **2** / **5** | product honesty |
| FALSE_HIT | **0**/10 | any → KILL |
| Decision | **HOLD** | — |

## Finding

1. Dual-arm LOOKUP + refuse-or-continue DECODE under max safe CPU (`cpus-2`).  
2. Span-fallback labeled **PEAK** (not DECODE gen credit); true_continue=0/10; span_fallback=3/10.  
3. True-gen judge = short-answer F1/HITL on **true continue** only — gold-substring / truncate-to-span ≠ gen IQ.  
4. Generative claim lifts **only** on true_continue_ablated PROMOTE (≥5.5) — honest HOLD accepted.  
5. AU H-NANOGEN5 STRICT 5.5 archive stays locked; AV3 is harder reopen; next AV4 AV-REAL-EVAL.

## Reproduce

```bash
npm run nano:nanogen6
npm run nano:nanogen5
```

## Artifacts

- Summary: `results/nano-lm/wave-av/nanogen6_summary.json`  
- Contract: `nano_lm/tests/test_nanogen6.py`

## Claims

| Allowed | Forbidden |
|---------|-----------|
| Honest HOLD on true_continue <5.5 | LOOKUP-as-gen-IQ |
| Span-fallback as PEAK/LOOKUP | Truncate-as-gen PROMOTE |
| PROMOTE only true_continue≥5.5 | NANOGEN5 5.5 truncate clone · Wave AW invent |

Next: **AV4 AV-REAL-EVAL** — product + gen with anti-FP law.
