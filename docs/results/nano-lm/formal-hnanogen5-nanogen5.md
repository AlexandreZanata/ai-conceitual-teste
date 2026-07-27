# H-NANOGEN5 — ablated generative lift (**DONE** — PROMOTE)

> Lab: `.local/pesquisa.md` §5 AU3 · Session: `.local/wave-au/SESSION.md`  
> Parent: [formal-hnanogen4-nanogen4.md](formal-hnanogen4-nanogen4.md) (ablated **5.5**) · Pack: NANOGEN held-out+para · STRICT F1/HITL  
> Module: `nano_lm/src/nanogen5_ops.py` · Runner: `npm run nano:nanogen5`

## Hypothesis

One idea: ablated DECODE with snippet-prefix + gibberish-tail gate (truncate/refuse when continuation leaves retrieved-span readability) scored by short-answer F1/HITL — gold-substring alone insufficient; beat archived NANOGEN4 ablated 5.5 under STRICT judge; bar = strict_ablated≥5.5 else HOLD

## Gate

| Metric | Result | Pass bar |
|--------|-------:|----------|
| LOOKUP mean | **9.0** | ≥ 7.0 |
| GENERATE ablated mean | **5.5** | ≥ **5.5** for PROMOTE |
| vs H-NANOGEN4 ablated | **5.5** | beats=True |
| GENERATE peak_on mean | **5.5** | compare only |
| bank-grounded mean | **5.5** | compare only (anti-FP) |
| n_snippet_prefix | **10** | ablated seed count |
| n_gibberish_truncated | **3** | tail truncated to span |
| peak_only_lift | **False** | peak≥5.5 ∧ ablated<5.5 → HOLD |
| n_abstain / n_bank_grounded | **2** / **5** | product honesty |
| FALSE_HIT | **0**/10 | any → KILL |
| Decision | **PROMOTE** | — |

## Finding

1. Dual-arm LOOKUP + ablated DECODE under max safe CPU (`cpus-2`).  
2. Ablated gate: snippet-prefix (10/10) + gibberish-tail truncate (3/10); bank-gold / peak stay **compare only**.  
3. STRICT judge = short-answer F1/HITL — gold-substring alone insufficient; gibberish-tail fails.  
4. Generative claim lifts **only** on strict_ablated PROMOTE (≥5.5) — not unlabeled peak-as-open-chat.  
5. AT H-NANOGEN4 PROMOTE (5.5 soft) stays locked; AU3 is STRICT reopen; next AU4 AU-REAL-EVAL.

## Reproduce

```bash
npm run nano:nanogen5
npm run nano:nanogen4
```

## Artifacts

- Summary: `results/nano-lm/wave-au/nanogen5_summary.json`  
- Contract: `nano_lm/tests/test_nanogen5.py`

## Claims

| Allowed | Forbidden |
|---------|-----------|
| Honest HOLD on strict <5.5 | LOOKUP-as-gen-IQ |
| Snippet-prefix + gibberish gate | Peak/bank-as-open-chat |
| PROMOTE only strict_ablated≥5.5 | gold-substring PROMOTE · Wave AV invent |

Next: **AU4 AU-REAL-EVAL** — product + gen with anti-FP law.
