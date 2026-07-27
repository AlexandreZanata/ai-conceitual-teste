# H-ADVFP — adversary false-hit suite (**DONE** — PROMOTE)

> Lab: `.local/pesquisa.md` §5 AQ2 · Session: `.local/wave-aq/SESSION.md`  
> Parent: [formal-hparahit-parahit.md](formal-hparahit-parahit.md) · Pack: AQ0 adversary-20  
> Module: `nano_lm/src/advfp_ops.py` · Runner: `npm run nano:advfp`

## Hypothesis

Near-miss · OOD · trap asks must **not** retrieve a wrong bank gold via SEMWRAP (false-hit **0**). Miss/DECODE is acceptable; silent LOOKUP of a near gold is **KILL**.

## Gate

| Metric | Result | Pass bar / rule |
|--------|-------:|-----------------|
| FALSE_HIT | **0**/20 | **0** (any → KILL) |
| SAFE | **20**/20 | — |
| mean score | **9.00** | informational |
| Decision | **PROMOTE** | false-hit=0 → PROMOTE |

## False-hit by kind

| kind | false-hits |
|------|----------:|
| near-miss | 0 |
| ood | 0 |
| trap | 0 |

## False-hit report

- (none)

## Finding

1. Adversary pack run through SEMWRAP with max CPU threads.  
2. Any LOOKUP / bank gold on an adversary ask counts as FALSE_HIT.  
3. Product safety metric only — **not** generative IQ / mini-AGI.

## Reproduce

```bash
npm run nano:advfp
npm run nano:z:ask -- --semwrap --question "Who won the 2014 FIFA World Cup final?"
```

## Artifacts

- Summary: `results/nano-lm/wave-aq/advfp_summary.json`  
- Trials: `results/nano-lm/wave-aq/trials/AQ-ADV-*.json`  
- Contract: `nano_lm/tests/test_advfp.py`

## Claims

| Allowed | Forbidden |
|---------|-----------|
| false-hit 0 on adversary-20 | Silent wrong-gold LOOKUP |
| MISS/DECODE on OOD/trap | Claiming refuse = generative IQ |
| Product safety gate | Wave AR invent |

Next: **AQ3 H-LATP** — **DONE PROMOTE** → [formal-hlatp-latp.md](formal-hlatp-latp.md).
