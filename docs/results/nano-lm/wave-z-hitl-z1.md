# Wave Z1 — HITL-10 baseline (**DONE** — FAIL pass bar)

> Lab: `.local/pesquisa.md` §9.4–9.5 · Live: `.local/wave-z/SESSION.md`  
> Champion: `champion-qpfb2-v0` · Ask mode: **QT + EARLY n=1** (no teacher self-grade)

## Gate

| Metric | Value | Pass bar |
|--------|------:|----------|
| mean score | **1.0** | ≥ 7.0 |
| errors | **10**/10 | ≤ 3/10 |
| Result | **FAIL** | continue → **Z2 WRAP** |

## Finding

Interactive ask under forced `temperature=1e-6` + EARLY gene collapses every completion to eight period tokens (`........`). Formal dual-gate / `code_teacher_lp` wins do **not** transfer to product Q&A on this serve path.

## Trials (all scored 1.0, `error=true`)

| id | source_id | domain | wall_ms (approx) |
|----|-----------|--------|-----------------:|
| Z1-01 | `python-tutorial-intro` | programming | ~150–200 |
| Z1-02 | `prog:g01` | programming | ~150–200 |
| Z1-03 | `python-tutorial-control` | programming | ~150–200 |
| Z1-04 | `rust-book-ch03` | programming | ~150–200 |
| Z1-05 | `bip-0001` | bitcoin | ~150–200 |
| Z1-06 | `bip-0032` | bitcoin | ~150–200 |
| Z1-07 | `bip-0141` | bitcoin | ~150–200 |
| Z1-08 | `python-tutorial-classes` | programming | ~150–200 |
| Z1-09 | `dom:d02` | howto | ~150–200 |
| Z1-10 | `bitcoin-core-readme` | bitcoin | ~150–200 |

Judge: Cursor frontier chat (`cursor-composer-frontier-chat`). Rubric bullets (each trial): period-only completion; no usable answer vs gold; in-scope / no harm issue.

## Error bank

- Path (gitignored): `results/nano-lm/wave-z/error_bank.jsonl`
- Rows: **10** (each with `gold` / `repaired` for Z2–Z3 fuel)
- Summary: `npm run nano:z:error-bank`

## Manual adjust (logged for Z2 — not applied mid-Z1)

Stop forcing ask `temperature=1e-6`; try EARLY gene temperature; relax early-exit for interactive ask; grow few-shot wrapper from error-bank golds.

## Reproduce

```bash
npm run nano:z:ask -- --trial Z1-01 --question "…"
npm run nano:z:log-trial -- results/nano-lm/wave-z/trials/Z1-01.json
npm run nano:z:error-bank
```

Warm batch: `ask_many` in `nano_lm/src/run_z_ask.py` (one CUDA load).

Next: **Z2 MANUAL×10** — wrapper/decode fixes from this bank, then 10 new trials.
