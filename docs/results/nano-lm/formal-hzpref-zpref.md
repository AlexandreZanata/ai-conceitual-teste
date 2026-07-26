# H-ZPREF — prefer gold≻raw (**DONE** — KILL)

> Lab: `.local/pesquisa.md` §8.1 AA3 · Wave AA  
> Parent: `champion-qpfb2-v0` · Bank ≥20 after WRAPBANK · Wrap still: `champion-wrap-v0`

## Hypothesis

Preference (DPO-lite rank): prefer error-bank **gold** over **model_raw** (or `........` fallback) without MIXD; keep story ≥ parent−ε; Z-HITL wrap LOOKUP still works.

## Gate

| Metric | Result | Rule |
|--------|-------:|------|
| bank rows | **20** | ≥ 20 |
| pref pairs | **20** | ≥ 10 |
| params | 3 348 928 | ≤ 5M |
| parent story_lp | **−15.318** | — |
| parent−ε floor | **−15.368** | ε=0.05 |
| H-ZPREF story_lp | **−15.414** | ≥ floor |
| wrap LOOKUP verify | **ok** | required |
| Decision | **KILL** | story below parent−ε |

Milder smokes (β=0.25/20 steps; β=0.1/8 steps) also **KILL** (story worse or still under floor). Wrap verify stayed green.

## Finding

1. Rank prefer gold≻raw on this ≤5M QT∘EARLY stack **regresses TinyStories story_lp** vs exported champion.  
2. Known-ask **H-ZWRAP** LOOKUP is unaffected (bank-side).  
3. Do **not** claim preference retrain fixes open decode or paraphrases (see H-PARA HOLD).  
4. Product path remains **H-ZWRAP** + WRAPBANK golds; **H-ZERR** stays the story-safer CE precedent.

## Reproduce

```bash
npm run nano:zpref -- --steps 40 --seed 0
npm run nano:z:ask -- --wrap --root results/nano-lm/wave-aa/models/zpref --question "…"
```

## Artifacts

- Module: `nano_lm/src/zpref_ops.py` · Train: `zpref_train.py` · Runner: `run_zpref.py`
- Summary: `results/nano-lm/wave-aa/zpref_summary.json`
- Ckpt (KILL evidence): `results/nano-lm/wave-aa/models/zpref/`
- Contract: `nano_lm/tests/test_zpref.py`

Next allowed: **H-DEPL-DOC** (AA4) — **DONE PROMOTE** → [formal-hdepldoc-depl-doc.md](formal-hdepldoc-depl-doc.md).
