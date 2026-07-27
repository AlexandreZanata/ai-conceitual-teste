# H-NANOGEN3 — ablated generative lift (**DONE** — HOLD)

> Lab: `.local/pesquisa.md` §5 AS7 · Session: `.local/wave-as/SESSION.md`  
> Parent: [formal-hnanogen2-nanogen2.md](formal-hnanogen2-nanogen2.md) (ablated **4.3**) · Pack: NANOGEN held-out+para  
> Module: `nano_lm/src/nanogen3_ops.py` · Runner: `npm run nano:nanogen3`

## Hypothesis

One idea: ablated DECODE with bank-grounded short continuation plus ASKABSTAIN refuse-junk on default ask path — score only mode=DECODE; beat NANOGEN2 ablated 4.3; bar = ablated≥5.0

## Gate

| Metric | Result | Pass bar |
|--------|-------:|----------|
| LOOKUP mean | **9.0** | ≥ 7.0 |
| GENERATE ablated mean | **4.3** | ≥ **5.0** for PROMOTE |
| vs H-NANOGEN2 ablated | **4.3** | beats=False |
| GENERATE peak_on mean | **6.5** | compare only |
| bank-grounded mean | **6.3** | compare only (anti-FP) |
| peak_only_lift | **True** | peak≥5 ∧ ablated<5 → HOLD |
| n_abstain / n_bank_grounded | **2** / **5** | product honesty |
| FALSE_HIT | **0**/10 | any → KILL |
| Decision | **HOLD** | — |

## Finding

1. Dual-arm LOOKUP + ablated DECODE under max safe CPU (`cpus-2`).  
2. Junk DECODE → ABSTAIN/NO_ANSWER; bank-grounded short is **compare only** (not ablated true-gen).  
3. Generative ship language lifts **only** on ablated PROMOTE.  
4. Peak / bank-grounded lift alone → HOLD (not open-chat IQ).  
5. AR H-NANOGEN2 HOLD (4.3) stays locked; AS7 is the reopen gate.

## Reproduce

```bash
npm run nano:nanogen3
npm run nano:nanogen2
```

## Artifacts

- Summary: `results/nano-lm/wave-as/nanogen3_summary.json`  
- Contract: `nano_lm/tests/test_nanogen3.py`

## Claims

| Allowed | Forbidden |
|---------|-----------|
| Honest HOLD on ablated <5 | LOOKUP-as-gen-IQ |
| Peak/bank compare labeled | Peak/bank-as-open-chat |
| PROMOTE only ablated≥5 | mini-AGI · Wave AT invent |

Next: **AS8 AS-DUAL-HITL** — **DONE PROMOTE** → [wave-as-dual-hitl.md](wave-as-dual-hitl.md) (product pass · gen locked). **AS9 AS-REPORT** — **DONE PROMOTE** → [wave-as-summary.md](wave-as-summary.md). Next: **AS10 AS-FREEZE**.
