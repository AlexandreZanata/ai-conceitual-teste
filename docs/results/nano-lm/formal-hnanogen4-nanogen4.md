# H-NANOGEN4 — ablated generative lift (**DONE** — PROMOTE)

> Lab: `.local/pesquisa.md` §5 AT3 · Session: `.local/wave-at/SESSION.md`  
> Parent: [formal-hnanogen3-nanogen3.md](formal-hnanogen3-nanogen3.md) (ablated **4.3**) · Pack: NANOGEN held-out+para  
> Module: `nano_lm/src/nanogen4_ops.py` · Runner: `npm run nano:nanogen4`

## Hypothesis

One idea: ablated DECODE with retrieved-snippet prefix conditioning (seed decode from top SEMWRAP/RAG span; student continues ≤N tokens) — no bank-gold rewrite, no peak overlay on gate score; beat NANOGEN3 ablated 4.3; bar = ablated≥5.0

## Gate

| Metric | Result | Pass bar |
|--------|-------:|----------|
| LOOKUP mean | **9.0** | ≥ 7.0 |
| GENERATE ablated mean | **5.5** | ≥ **5.0** for PROMOTE |
| vs H-NANOGEN3 ablated | **4.3** | beats=True |
| GENERATE peak_on mean | **6.5** | compare only |
| bank-grounded mean | **6.5** | compare only (anti-FP) |
| n_snippet_prefix | **10** | ablated seed count |
| peak_only_lift | **False** | peak≥5 ∧ ablated<5 → HOLD |
| n_abstain / n_bank_grounded | **0** / **5** | product honesty |
| FALSE_HIT | **0**/10 | any → KILL |
| Decision | **PROMOTE** | — |

## Finding

1. Dual-arm LOOKUP + ablated DECODE under max safe CPU (`cpus-2`).  
2. Ablated gate used retrieved-snippet prefix on **10/10** trials (RAG
   extractive seed + student continue text); bank-gold / peak overlay stay
   **compare only** (`peak_used=false` on gate).  
3. Ablated mean **5.5** ≥ **5.0** (parent NANOGEN3 **4.3**) → **PROMOTE**.  
4. Peak compare **6.5** / bank compare **6.5** — labeled, not the gate.  
5. Claim = **ablated DECODE with snippet-prefix conditioning** — not
   LOOKUP-as-IQ · not unlabeled peak-as-open-chat · not mini-AGI open chat
   until AT-REAL-EVAL.  
6. AS H-NANOGEN3 HOLD (4.3) stays locked; AT3 is the reopen gate.

## Reproduce

```bash
npm run nano:nanogen4
npm run nano:nanogen3
```

## Artifacts

- Summary: `results/nano-lm/wave-at/nanogen4_summary.json`  
- Contract: `nano_lm/tests/test_nanogen4.py`

## Claims

| Allowed | Forbidden |
|---------|-----------|
| Honest HOLD on ablated <5 | LOOKUP-as-gen-IQ |
| Snippet-prefix on ablated labeled | Peak/bank-as-open-chat |
| PROMOTE only ablated≥5 | mini-AGI · Wave AU invent |

Next: **AT4 AT-REAL-EVAL** — product + gen with anti-FP law.
