# H-NANOGEN2 — ablated generative lift (**DONE** — HOLD)

> Lab: `.local/pesquisa.md` §5 AR5 · Session: `.local/wave-ar/SESSION.md`  
> Parent: [formal-hnanogen-nanogen.md](formal-hnanogen-nanogen.md) (ablated **4.0**) · Pack: NANOGEN held-out+para  
> Module: `nano_lm/src/nanogen2_ops.py` · Runner: `npm run nano:nanogen2`

## Hypothesis

One idea: ablated DECODE with bank-grounded short continuation plus refuse-junk gate (ABSTAIN/NO_ANSWER on OOD/miss garbage) — score only mode=DECODE; peak remains compare-only; bar = ablated≥5.0

## Gate

| Metric | Result | Pass bar |
|--------|-------:|----------|
| LOOKUP mean | **9.0** | ≥ 7.0 |
| GENERATE ablated mean | **4.3** | ≥ 5.0 for PROMOTE |
| vs H-NANOGEN ablated | **4.0** | beats=True |
| GENERATE peak_on mean | **6.5** | compare only |
| bank-grounded mean | **6.3** | compare only (anti-FP) |
| peak_only_lift | **True** | peak≥5 ∧ ablated<5 → HOLD |
| n_abstain / n_bank_grounded | **2** / **5** | product honesty |
| FALSE_HIT | **0**/10 | any → KILL |
| Decision | **HOLD** | — |

## Finding

1. Dual-arm LOOKUP + ablated DECODE under max safe CPU (`cpus-2`).  
2. Junk DECODE → ABSTAIN/NO_ANSWER (product); bank-grounded short is **compare only** (not ablated true-gen).  
3. Generative ship language lifts **only** on ablated PROMOTE.  
4. Peak / bank-grounded lift alone → HOLD (not open-chat IQ).

## Reproduce

```bash
npm run nano:nanogen2
npm run nano:nanogen
```

## Artifacts

- Summary: `results/nano-lm/wave-ar/nanogen2_summary.json`  
- Contract: `nano_lm/tests/test_nanogen2.py`

## Claims

| Allowed | Forbidden |
|---------|-----------|
| Honest HOLD on ablated <5 | LOOKUP-as-gen-IQ |
| Peak/bank compare labeled | Peak/bank-as-open-chat |
| PROMOTE only ablated≥5 | mini-AGI · Wave AS invent |

Next: **AR6 AR-DUAL-HITL** — **DONE HOLD** → [wave-ar-dual-hitl.md](wave-ar-dual-hitl.md). Next **AR7 AR-REPORT**.
