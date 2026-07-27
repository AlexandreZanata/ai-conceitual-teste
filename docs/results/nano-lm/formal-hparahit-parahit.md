# H-PARAHIT — paraphrase SEMWRAP hit-rate (**DONE** — PROMOTE)

> Lab: `.local/pesquisa.md` §5 AQ1 · Session: `.local/wave-aq/SESSION.md`  
> Parent: [wave-aq-session.md](wave-aq-session.md) (AQ0 packs) · **H-SEMWRAP**  
> Module: `nano_lm/src/parahit_ops.py` · Runner: `npm run nano:parahit`

## Hypothesis

Human-written paraphrases of known golds (AQ0 paraphrase-20) recover via **SEMWRAP** without false-hits — measuring real paraphrase robustness, **not** LOOKUP-as-IQ and **not** by banking the paraphrase text first.

## Gate

| Metric | Result | Pass bar / rule |
|--------|-------:|-----------------|
| hit_rate (TRUE_HIT) | **0.95** (19/20) | ≥ **0.7** |
| mean score | **8.75** | ≥ **7.0** |
| FALSE_HIT | **0**/20 | **0** (any → KILL) |
| MISS | **1**/20 | report |
| Decision | **PROMOTE** | hit∧mean ∧ false-hit=0 |

## Miss report

- `AQ-PARA-02`

## Finding

1. Parents seeded only when missing; paraphrases **not** pre-banked (anti memorization theater).  
2. Product path labeled LOOKUP / SEMWRAP_LOOKUP — **not** generative IQ.  
3. Next generative claim still gated by **AQ6 H-NANOGEN** ablated bar.

## Reproduce

```bash
npm run nano:parahit
npm run nano:z:ask -- --semwrap --question "<AQ-PARA paraphrase>"
```

## Artifacts

- Summary: `results/nano-lm/wave-aq/parahit_summary.json`  
- Trials: `results/nano-lm/wave-aq/trials/AQ-PARA-*.json`  
- Contract: `nano_lm/tests/test_parahit.py`

## Claims

| Allowed | Forbidden |
|---------|-----------|
| Product paraphrase hit-rate on SEMWRAP | LOOKUP mean as generative IQ |
| Honest HOLD when hit_rate < bar | Expand bank until HITL memorizes paras |
| false-hit 0 as hard law | Open chat / mini-AGI claim |

Next: **AQ2 H-ADVFP** — **DONE PROMOTE** → [formal-hadvfp-advfp.md](formal-hadvfp-advfp.md).
