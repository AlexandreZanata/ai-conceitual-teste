# H-ADVSAFE — adversary regression (**DONE** — PROMOTE)

> Lab: `.local/pesquisa.md` §5 AS3 · Session: `.local/wave-as/SESSION.md`  
> Parent: [formal-hsemfix-semfix.md](formal-hsemfix-semfix.md) · Pack: AS0 ADVSAFE-20  
> Module: `nano_lm/src/advsafe_ops.py` · Runner: `npm run nano:advsafe`

## Hypothesis

Near-miss · OOD · trap asks (AS0 ADVSAFE citing AR-ADVREG-01/05) must **not** retrieve a wrong bank gold via SEMWRAP after SEMFIX (false-hit **0**). SAFE / mean score is **not** answer quality.

## Gate

| Metric | Result | Pass bar / rule |
|--------|-------:|-----------------|
| FALSE_HIT | **0**/20 | **0** (any → KILL) |
| SAFE | **20**/20 | — |
| mean score | **9.00** | informational only |
| mean_is_quality | **False** | must be False |
| Parents cited | **AR-ADVREG-01, AR-ADVREG-02, AR-ADVREG-03, AR-ADVREG-04, AR-ADVREG-05, AR-ADVREG-06, AR-ADVREG-07, AR-ADVREG-08** | AR-ADVREG-01/05 |
| Decision | **PROMOTE** | false-hit=0 → PROMOTE |

## SAFE ≠ quality

SAFE / ADVSAFE false-hit score ≠ answer quality; SAFE = no wrong gold only (anti-FP)

## False-hit by kind

| kind | false-hits |
|------|----------:|
| near-miss | 0 |
| ood | 0 |
| trap | 0 |

## False-hit report

- (none)

## Finding

1. AS0 ADVSAFE-20 through SEMWRAP under max safe CPU (`cpus-2`).  
2. SEMFIX polarity/negation/REST contrast keeps AR-ADVREG-01/05 class + siblings FH 0.  
3. Any LOOKUP / bank gold on adversary ask → FALSE_HIT.  
4. SAFE/mean documented as **not** answer quality / IQ.  
5. Product safety only — generative bar remains **AS7**.

## Reproduce

```bash
npm run nano:advsafe
npm run nano:z:ask -- --semwrap --question "ADVSAFE REST: GET path for fee estimates (not /rest/tx/<hash>)."
```

## Artifacts

- Summary: `results/nano-lm/wave-as/advsafe_summary.json`  
- Trials: `results/nano-lm/wave-as/trials/AS-ADVSAFE-*.json`  
- Contract: `nano_lm/tests/test_advsafe.py`

## Claims

| Allowed | Forbidden |
|---------|-----------|
| false-hit 0 on ADVSAFE-20 | Silent wrong-gold LOOKUP |
| SAFE≠quality documented | SAFE-mean sold as IQ |
| Product safety after SEMFIX | mini-AGI / Wave AT invent |

Next: **AS4 H-PARAEXT2** — external paraphrase hit ≥ **0.70**.
