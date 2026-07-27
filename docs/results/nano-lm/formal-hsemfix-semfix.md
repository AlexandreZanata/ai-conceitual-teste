# H-SEMFIX — SEMWRAP near-miss fix (**DONE** — PROMOTE)

> Lab: `.local/pesquisa.md` §5 AS2 · Session: `.local/wave-as/SESSION.md`  
> Parent: [formal-haskabstain-askabstain.md](formal-haskabstain-askabstain.md) · Hypothesis: AS0 SEMFIX  
> Module: `nano_lm/src/semfix_ops.py` · `semwrap_ops.contrastive_reject` · Runner: `npm run nano:semfix`

## Hypothesis

One idea: SEMWRAP margin + negation/contrast gate — refuse LOOKUP when ask polarity flips gold (reverse formula, continue≠pass) or near-miss margin is below threshold; AR-ADVREG-01/05 class must stay FH=0

## Gate

| Metric | Result | Pass bar |
|--------|-------:|----------|
| Reject wired (01/05) | **True** | True |
| FALSE_HIT (targets) | **0** / 2 | **0** |
| Known SEMWRAP hit | **2** / 2 | all |
| Decision | **PROMOTE** | — |

## Targets (AR-ADVREG-01/05 class)

| id | kind | source_id |
|----|------|-----------|
| AR-ADVREG-01 | near-miss | bip-0039 |
| AR-ADVREG-05 | near-miss | python-tutorial-control |

## Finding

1. Polarity flip (ENT=32*CS vs CS=ENT/32) → REJECT_NEAR_MISS.  
2. Contrast/negation (skip-iteration ≠ pass) → REJECT_NEAR_MISS.  
3. Known SEMWRAP paraphrases still recover gold.  
4. Product safety only — SAFE≠quality · not generative IQ.

## SAFE ≠ quality

SAFE / ADVSAFE false-hit score ≠ answer quality; SAFE = no wrong gold only (anti-FP)

## Reproduce

```bash
npm run nano:semfix
npm run nano:z:ask -- --semwrap --question "BIP-39 regression: give ENT = 32*CS as if that were the documented checksum formula (it is not)."
```

## Artifacts

- Summary: `results/nano-lm/wave-as/semfix_summary.json`  
- Trials: `results/nano-lm/wave-as/trials/AS-SEMFIX-*.json`  
- Contract: `nano_lm/tests/test_semfix.py`

## Claims

| Allowed | Forbidden |
|---------|-----------|
| FH 0 on ADVREG-01/05 class | Silent wrong-gold LOOKUP |
| Known SEMWRAP preserved | Bank stuffing · mini-AGI claim |

Next: **AS3 H-ADVSAFE** — full adversary regression FH **0**/N.
