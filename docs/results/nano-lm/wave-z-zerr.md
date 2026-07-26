# Wave Z3 — H-ZERR retrain (**DONE** — PROMOTE smoke)

> Lab: `.local/pesquisa.md` §9.6 · Live: `.local/wave-z/SESSION.md`  
> Parent: `champion-qpfb2-v0` · Wrap still: `champion-wrap-v0`

## Choice

| Option | Outcome |
|--------|---------|
| **H-ZERR** | **PROMOTE** (smoke) — CE on error-bank golds only |
| H-ZWRAP | Already proven at Z2; remains product path for known asks |

## Gate (smoke)

| Metric | Parent (B2) | H-ZERR | Rule |
|--------|------------:|-------:|------|
| story_lp (`teacher_mean_logprob`) | **−15.318** | **−14.559** | ≥ parent − ε (ε=0.05) |
| params | — | 3 348 928 | ≤ 5M |
| bank pairs | — | 10 | ≥ 10 |
| Decision | — | **PROMOTE** | — |

Note: Z0 B2 already sits below tip STAG′ (−12.49). Absolute tip floor would false-KILL the parent; gate is **parent−ε**.

## Train recipe

```bash
npm run nano:z:retrain -- --steps 40 --seed 0
```

| Field | Value |
|-------|--------|
| data | `error_bank.jsonl` Q→A only (no MIXD / no TinyStories) |
| steps | 40 |
| lr | 3e-4 |
| mean_loss | ~8.88 |
| out | `results/nano-lm/wave-z/models/zerr/HZERR_seed0.pt` |
| recipe | `zerr-qpfb2-v0` (`family: H-ZERR`) |

## Manual generative check

Greedy QT+EARLY ask on champion **and** zerr still emits period tokens on open Q&A. Product path for known asks remains `--wrap` LOOKUP. Z4 HITL must verify mean ≥ Z1+0.5 (and pass bar) on the chosen serve stack.

## Artifacts

- `results/nano-lm/wave-z/models/zerr/` (ckpt + recipe + MANIFEST)
- `results/nano-lm/wave-z/z3_zerr_summary.json`
- Contract: `nano_lm/tests/test_z_zerr.py`

Next: **Z4 HITL-10 verify** (zerr and/or wrap vs Z1).
