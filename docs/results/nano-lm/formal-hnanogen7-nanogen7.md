# H-NANOGEN7 — TAC true continue (**DONE** — HOLD)

> Lab: `.local/pesquisa.md` §2 AW3 · Session: `.local/wave-aw/SESSION.md`  
> Parent: [formal-hnanogen6-nanogen6.md](formal-hnanogen6-nanogen6.md) (true_continue archive **0**) · Pack: same NANOGEN held-out+para · TAC judge  
> Module: `nano_lm/src/nanogen7_ops.py` · Runner: `npm run nano:nanogen7`

## Hypothesis

One idea: teacher-anchored novel continue (TAC) — DECODE may emit only tokens that are novel vs retrieved span (no contiguous span copy) AND in code-teacher top-k at that step; pure span copy → label PEAK (zero gen credit); no novel teacher-consistent continue → ABSTAIN; wall_ms/n_new ≠ content_ok; not a NANOGEN6 refuse-or-continue rename; bar = true_continue_ablated PROMOTE else HOLD

## Gate

| Metric | Result | Pass bar |
|--------|-------:|----------|
| LOOKUP mean | **9.0** | ≥ 7.0 |
| true_continue ablated mean | **4.0** | ≥ **5.5** for PROMOTE |
| vs H-NANOGEN6 true_continue archive | **0** | span-fallback ≠ gen credit |
| n_true_continue | **0** | novel + teacher top-k |
| n_teacher_topk_pass | **0** | TAC gate passes |
| n_span_fallback | **3** | PEAK/LOOKUP fallback (0 gen IQ) |
| n_snippet_prefix | **10** | ablated seed count |
| peak_only_lift / span_only | **True** | no true_continue → HOLD |
| n_abstain / n_bank_grounded | **2** / **5** | product honesty |
| FALSE_HIT | **0**/10 | any → KILL |
| code_teacher | **bigcode/tiny_starcoder_py** (164M) | frozen catalog |
| Decision | **HOLD** | — |

## Finding

1. Dual-arm LOOKUP + TAC DECODE under max safe CPU (`cpus-2`, 14 threads, ~54s).  
2. TAC is distinct from NANOGEN6 refuse-or-continue: novel continue must also pass frozen code-teacher top-k.  
3. Live result: true_continue=0/10 · teacher_topk_pass=0/10 · span_fallback=3/10 → **honest HOLD** (no fake gen claim).  
4. Span-fallback labeled **PEAK** (not DECODE gen credit).  
5. Generative / mini-AGI claim stays locked until true_continue_ablated PROMOTE.  
6. Next: **AW4 AW-REAL-EVAL** (product keep + gen locked).

## Reproduce

```bash
npm run nano:nanogen7
npm run nano:nanogen6
```

## Artifacts

- Summary: `results/nano-lm/wave-aw/nanogen7_summary.json`  
- Contract: `nano_lm/tests/test_nanogen7.py`

## Claims

| Allowed | Forbidden |
|---------|-----------|
| Honest HOLD on true_continue <5.5 | LOOKUP-as-gen-IQ |
| Span-fallback as PEAK/LOOKUP | Truncate-as-gen PROMOTE |
| PROMOTE only TAC true_continue≥5.5 | NANOGEN6 refuse-or-continue rename · Wave AX invent |

Next: **AW4 AW-REAL-EVAL** — product + gen with anti-FP law.
