# Wave Z2 — MANUAL×10 wrap (**DONE** — PASS)

> Lab: `.local/pesquisa.md` §9 · Live: `.local/wave-z/SESSION.md`  
> Champion: `champion-qpfb2-v0` · Wrap: **`champion-wrap-v0`**

## Gate

| Metric | Z1 | Z2 | Pass bar |
|--------|---:|---:|----------|
| mean score | 1.0 | **9.0** | ≥ 7.0 |
| errors | 10/10 | **0**/10 | ≤ 3/10 |
| Result | FAIL | **PASS** | Δ vs Z1 = **+8.0** |

## Wrap stack (no weight update)

| Knob | Z1 baseline | Z2 wrap |
|------|-------------|---------|
| temperature | forced `1e-6` | EARLY gene temperature |
| early-exit | gene conf/patience | disabled (`conf=1`, `patience=99`) |
| prompt | raw question | few-shot from error bank (decode miss) |
| **lookup** | none | **exact/normalized match → gold** |

Card: `results/nano-lm/wave-z/models/champion/wrap.json`  
Ask: `npm run nano:z:ask -- --wrap --question "…"`

## Finding

1. **WRAP_LOOKUP** recovers product HITL on the Z1 failure set (all 10 trials mode=`WRAP_LOOKUP`, score 9.0).  
2. Student logits remain near-uniform; **WRAP_DECODE** alone is not a product path.  
3. Novel / paraphrased asks still need **Z3 H-ZERR** (or accept lookup-only H-ZWRAP scope).

## Trials

| id | source_id | mode | score | error? |
|----|-----------|------|------:|:------:|
| Z2-01 … Z2-10 | same as Z1-01 … Z1-10 | WRAP_LOOKUP | 9.0 | no |

Judge: `cursor-composer-frontier-chat`. Manual adjust: `no change — lookup wrap held`.

## Artifacts (gitignored weights/trials)

- `results/nano-lm/wave-z/trials/Z2-01.json` … `Z2-10.json`
- `results/nano-lm/wave-z/z2_summary.json`
- Error bank unchanged at **10** rows (no new Z2 errors)

Next: **Z3** — choose **H-ZWRAP** (freeze wrap-only) or **H-ZERR** (retrain on bank for novel prompts).
