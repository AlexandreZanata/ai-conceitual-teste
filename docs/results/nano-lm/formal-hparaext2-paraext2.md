# H-PARAEXT2 — external paraphrase after SEMFIX (**DONE** — PROMOTE)

> Lab: `.local/pesquisa.md` §5 AS4 · Session: `.local/wave-as/SESSION.md`  
> Parent: [formal-hadvsafe-advsafe.md](formal-hadvsafe-advsafe.md) · Pack: AS0 PARAEXT2-20  
> Module: `nano_lm/src/paraext2_ops.py` · Runner: `npm run nano:paraext2`

## Hypothesis

Fresh AS0 PARAEXT2 paraphrases (≠ AQ-PARA / AR-EXT / AP-HITL) recover via **SEMWRAP** after SEMFIX without false-hits — real paraphrase robustness, **not** bank-stuffed theater and **not** generative IQ.

## Gate

| Metric | Result | Pass bar / rule |
|--------|-------:|-----------------|
| hit_rate (TRUE_HIT) | **0.8** (16/20) | ≥ **0.7** |
| mean score | **8.00** | ≥ **7.0** |
| FALSE_HIT | **0**/20 | **0** (any → KILL) |
| MISS | **4**/20 | report |
| Decision | **PROMOTE** | hit∧mean ∧ false-hit=0 |

## Miss report

- `AS-EXT2-01`
- `AS-EXT2-02`
- `AS-EXT2-07`
- `AS-EXT2-09`

## Finding

1. Parents seeded only when missing; paraphrases **not** pre-banked (anti memorization theater).  
2. Pack disjoint from AQ-PARA · AR-EXT · AP-HITL exact text.  
3. Product path labeled LOOKUP / SEMWRAP_LOOKUP — **not** generative IQ.  
4. AR H-PARAEXT HOLD (0.65) stays locked; AS4 is a fresh pack.  
5. Generative claim still gated by **AS7 H-NANOGEN3**.

## Reproduce

```bash
npm run nano:paraext2
npm run nano:z:ask -- --semwrap --question "Para-ext2: BIP-39 checksum length — write CS in terms of ENT."
```

## Artifacts

- Summary: `results/nano-lm/wave-as/paraext2_summary.json`  
- Trials: `results/nano-lm/wave-as/trials/AS-EXT2-*.json`  
- Contract: `nano_lm/tests/test_paraext2.py`

## Claims

| Allowed | Forbidden |
|---------|-----------|
| External paraphrase hit-rate on SEMWRAP | LOOKUP-as-IQ |
| Honest HOLD when hit_rate < bar | Bank stuffing |
| false-hit 0 as hard law | Rewrite AR PARAEXT |

Next: **AS5 H-METRICS** — **DONE PROMOTE** → [formal-hmetrics-metrics.md](formal-hmetrics-metrics.md).
