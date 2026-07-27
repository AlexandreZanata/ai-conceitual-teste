# H-ADVREG — adversary regression (**DONE** — KILL)

> Lab: `.local/pesquisa.md` §5 AR4 · Session: `.local/wave-ar/SESSION.md`  
> Parent: [formal-hparaext-paraext.md](formal-hparaext-paraext.md) · Pack: AR0 advreg-20  
> Module: `nano_lm/src/advreg_ops.py` · Runner: `npm run nano:advreg`

## Hypothesis

Near-miss · OOD · trap regression asks (≠ AQ-ADV exact text) must **not** retrieve a wrong bank gold via SEMWRAP (false-hit **0**). SAFE / mean score is **not** answer quality.

## Gate

| Metric | Result | Pass bar / rule |
|--------|-------:|-----------------|
| FALSE_HIT | **2**/20 | **0** (any → KILL) |
| SAFE | **18**/20 | — |
| mean score | **8.10** | informational only |
| mean_is_quality | **False** | must be False |
| Decision | **KILL** | false-hit=0 → PROMOTE |

## SAFE ≠ quality

SAFE / ADVFP / ADVREG false-hit score ≠ answer quality; SAFE = no wrong gold only (anti-FP)

## False-hit by kind

| kind | false-hits |
|------|----------:|
| near-miss | 2 |
| ood | 0 |
| trap | 0 |

## False-hit report

- `AR-ADVREG-01`
- `AR-ADVREG-05`

## Finding

1. AR0 advreg pack through SEMWRAP under max safe CPU (`cpus-2`).  
2. Any LOOKUP / bank gold on adversary ask → FALSE_HIT.  
3. SAFE/mean documented as **not** answer quality / IQ.  
4. Live: near-miss leaks `AR-ADVREG-01` (BIP-39 CS gold) · `AR-ADVREG-05` (Python `pass` vs continue) → **KILL**.  
5. Product safety only — generative bar remains **AR5**.

## Reproduce

```bash
npm run nano:advreg
npm run nano:z:ask -- --semwrap --question "Which nation hosted the 2016 Summer Olympics?"
```

## Artifacts

- Summary: `results/nano-lm/wave-ar/advreg_summary.json`  
- Trials: `results/nano-lm/wave-ar/trials/AR-ADVREG-*.json`  
- Contract: `nano_lm/tests/test_advreg.py`

## Claims

| Allowed | Forbidden |
|---------|-----------|
| false-hit 0 on advreg-20 | Silent wrong-gold LOOKUP |
| SAFE≠quality documented | SAFE-mean sold as IQ |
| Product safety gate | mini-AGI / Wave AS invent |

Next: **AR5 H-NANOGEN2** — **DONE HOLD** → [formal-hnanogen2-nanogen2.md](formal-hnanogen2-nanogen2.md). Next **AR6 AR-DUAL-HITL**.
