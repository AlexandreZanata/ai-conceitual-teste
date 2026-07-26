# H-PARA — paraphrase wrap stress (**DONE** — HOLD)

> Lab: `.local/pesquisa.md` §8.1 AA1 · Wave AA  
> Parent product: **H-ZWRAP** exact-match LOOKUP · No weight update

## Hypothesis

Paraphrase the Z1–Z4 known asks; `--wrap` **must not false-hit** a wrong bank gold. Gate: HITL mean≥7 **or** document exact-match lookup brittleness.

## Gate

| Metric | Result | Pass bar / rule |
|--------|-------:|-----------------|
| mean score | **4.0** | ≥ 7.0 for PROMOTE |
| errors | **10**/10 | ≤ 3 for PROMOTE |
| FALSE_HIT | **0**/10 | any → **KILL** |
| MISS | **10**/10 | expected under exact normalize |
| TRUE_HIT | **0**/10 | — |
| Decision | **HOLD** | document brittleness (allowed) |

## Finding

1. **No false-hits** — paraphrases never returned a wrong bank gold via `normalize_question` exact match.  
2. All 10 trials **MISS** → `WRAP_DECODE` (few-shot); completions ≠ parent gold (score 4.0), not period-only.  
3. Product claim stays honest: **H-ZWRAP = exact known-ask LOOKUP**, not paraphrase-robust Q&A.  
4. Do **not** claim wrap “understands” reworded questions without bank growth / fuzzy match (out of scope here).

## Pack

Paraphrases of Z1-01…Z1-10 (`python-tutorial-*`, `prog:g01`, `rust-book-ch03`, BIP/Core, `dom:d02`). See `para_ops.PARA_PACK`.

## Reproduce

```bash
npm run nano:para
npm run nano:z:ask -- --wrap --question "<paraphrase>"
# compare exact parent → WRAP_LOOKUP
```

## Artifacts

- Module: `nano_lm/src/para_ops.py` · Runner: `nano_lm/src/run_para.py`
- Summary: `results/nano-lm/wave-aa/para_summary.json`
- Trials: `results/nano-lm/wave-aa/trials/AA1-01.json` … `AA1-10.json`
- Contract: `nano_lm/tests/test_para.py`

Next allowed: **H-ZPREF** (bank≥20) or **H-DEPL-DOC** / **H-SERVEALIGN** if open decode desired.
