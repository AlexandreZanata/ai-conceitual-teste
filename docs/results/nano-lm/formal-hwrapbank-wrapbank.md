# H-WRAPBANK — expand wrap golds (**DONE** — PROMOTE)

> Lab: `.local/pesquisa.md` §8.1 AA0 · Wave AA  
> Parent product: **H-ZWRAP** (`champion-wrap-v0`) · No weight update

## Hypothesis

Expand `error_bank.jsonl` / wrap golds with **10 new scoped Q→gold** pairs from curated sources; HITL×10 on `--wrap` must pass the stage bar **without** student weight update.

## Gate

| Metric | Result | Pass bar |
|--------|-------:|----------|
| mean score | **9.0** | ≥ 7.0 |
| errors | **0**/10 | ≤ 3/10 |
| WRAP_LOOKUP | **10**/10 | product path |
| weight update | **false** | required |
| Decision | **PROMOTE** | — |

## Pack (source_ids)

| id | source_id |
|----|-----------|
| AA0-01 | `bip-0039` |
| AA0-02 | `bip-0340` |
| AA0-03 | `python-tutorial-datastructures` |
| AA0-04 | `python-tutorial-io` |
| AA0-05 | `rust-book-ch03-02` |
| AA0-06 | `rust-book-ch04-01` |
| AA0-07 | `rust-book-ch05-01` |
| AA0-08 | `bitcoin-json-rpc` |
| AA0-09 | `bitcoin-rest` |
| AA0-10 | `bitcoin-doc-bips` |

## Reproduce

```bash
npm run nano:wrapbank
npm run nano:z:ask -- --wrap --question "…"
```

## Finding

1. Bank grew **10 → 20** rows (idempotent re-run adds 0).  
2. All 10 new asks hit **WRAP_LOOKUP** (mean 9.0) — same product contract as Z2/Z4.  
3. Still **not** an open chat LM; novel paraphrases remain **H-PARA** (AA1).

## Artifacts

- Module: `nano_lm/src/wrapbank_ops.py` · Runner: `nano_lm/src/run_wrapbank.py`
- Summary: `results/nano-lm/wave-aa/wrapbank_summary.json` (gitignored tree)
- Trials: `results/nano-lm/wave-aa/trials/AA0-01.json` … `AA0-10.json`
- Contract: `nano_lm/tests/test_wrapbank.py`

Next allowed: **H-PARA** (AA1) — **DONE HOLD** → [formal-hpara-para.md](formal-hpara-para.md). Then **H-ZPREF** if bank≥20.
