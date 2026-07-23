# Nano-LM smoke results (phase 10)

Frozen baseline: `roneneldan/TinyStories-1M` (Eldan & Li, [arXiv:2305.07759](https://arxiv.org/abs/2305.07759)).

## Run provenance

| Item | Path / value |
|------|----------------|
| Config | `nano_lm/configs/smoke.json` |
| Prompts | `nano_lm/prompts/smoke_prompts.yaml` (p01, p02) |
| Seeds | 0, 1 |
| Raw JSONL | `results/nano-lm/smoke/runs.jsonl` (gitignored) |
| Meta | `results/nano-lm/smoke/meta.json` — `n_rows=12` |
| Aggregate table | [smoke-summary.md](smoke-summary.md) / [smoke-summary.csv](smoke-summary.csv) |

## Smoke comparison (self mean log-prob; higher is better)

| method | mean_logprob | mean wall_ms | mean token_evals | win_rate_vs_ar |
|--------|--------------|--------------|------------------|----------------|
| ar | −1.11 | ~350 | 64 | — |
| bon | −0.75 | ~1930 | 512 | 1.00 |
| mae | −0.70 | ~13100 | 3072 | 1.00 |

On this smoke slice, **BoN and Lookahead MAE both beat AR** on length-normalized self log-prob on every (prompt, seed) pair. MAE edges BoN slightly on mean log-prob but costs ~7× wall time and 6× token-evals vs BoN (~40× vs AR).

## Limits

- Smoke uses **2 prompts**, not the full 8-prompt formal set.
- No GPT-4 teacher grading (paper paradigm); self log-prob only.
- Formal bench: `npm run nano:bench` → `nano_lm/configs/bench.json` (optional teacher `TinyStories-33M`).

Protocol: [docs/NANO-LM-TRACK.md](../../NANO-LM-TRACK.md).
