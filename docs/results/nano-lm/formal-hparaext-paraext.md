# H-PARAEXT — external paraphrase SEMWRAP (**DONE** — HOLD)

> Lab: `.local/pesquisa.md` §5 AR3 · Session: `.local/wave-ar/SESSION.md`  
> Parent: [formal-hshipdemo-shipdemo.md](formal-hshipdemo-shipdemo.md) · Pack: AR0 external-para-20  
> Module: `nano_lm/src/paraext_ops.py` · Runner: `npm run nano:paraext`

## Hypothesis

Fresh external/human paraphrases (≠ AQ-PARA exact text) recover via **SEMWRAP** without false-hits — real paraphrase robustness, **not** AQ0 replay and **not** by banking the paraphrase text.

## Gate

| Metric | Result | Pass bar / rule |
|--------|-------:|-----------------|
| hit_rate (TRUE_HIT) | **0.65** (13/20) | ≥ **0.7** |
| mean score | **7.25** | ≥ **7.0** |
| FALSE_HIT | **0**/20 | **0** (any → KILL) |
| MISS | **7**/20 | report |
| Decision | **HOLD** | hit∧mean ∧ false-hit=0 |

## Miss report

- `AR-EXT-01`
- `AR-EXT-02`
- `AR-EXT-03`
- `AR-EXT-04`
- `AR-EXT-06`
- `AR-EXT-07`
- `AR-EXT-13`

## Finding

1. Parents seeded only when missing; paraphrases **not** pre-banked (anti memorization theater).  
2. Pack disjoint from AQ-PARA exact paraphrase text.  
3. Product path labeled LOOKUP / SEMWRAP_LOOKUP — **not** generative IQ.  
4. Generative claim still gated by **AR5 H-NANOGEN2**.

## Reproduce

```bash
npm run nano:paraext
npm run nano:z:ask -- --semwrap --question "<AR-EXT paraphrase>"
```

## Artifacts

- Summary: `results/nano-lm/wave-ar/paraext_summary.json`  
- Trials: `results/nano-lm/wave-ar/trials/AR-EXT-*.json`  
- Contract: `nano_lm/tests/test_paraext.py`

## Claims

| Allowed | Forbidden |
|---------|-----------|
| External paraphrase hit-rate on SEMWRAP | LOOKUP-as-IQ |
| Honest HOLD when hit_rate < bar | AQ0 paraphrase replay |
| false-hit 0 as hard law | Bank expand until theater |

Next: **AR4 H-ADVREG** — **DONE KILL** → [formal-hadvreg-advreg.md](formal-hadvreg-advreg.md). **AR6 AR-DUAL-HITL** — **DONE HOLD** → [wave-ar-dual-hitl.md](wave-ar-dual-hitl.md).
