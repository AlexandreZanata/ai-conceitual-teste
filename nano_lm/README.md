# nano_lm — TinyStories decode comparison track

Isolated Python/PyTorch research track (not part of the C++ EvoGen domain).

## Baseline

- Model: [`roneneldan/TinyStories-1M`](https://huggingface.co/roneneldan/TinyStories-1M) (&lt;50M params)
- Tokenizer: `EleutherAI/gpt-neo-125M`
- Paper: Eldan & Li, [arXiv:2305.07759](https://arxiv.org/abs/2305.07759)

## Methods

| ID | Behavior |
|----|----------|
| `ar` | Temperature + top-p next-token sampling |
| `bon` | Best-of-N full completions; pick max length-normalized log-prob |
| `mae` | Lookahead multi-attempt evaluate: K candidate blocks, score by H-token future mean log-prob, commit winner |

## Setup

```bash
python3 -m venv nano_lm/.venv
source nano_lm/.venv/bin/activate
pip install -r nano_lm/requirements.txt
```

## Terminal lab (live progress + GPU charts + comparison)

```bash
npm run nano:lab          # GPU-heavy config (batched BoN/MAE, fp16, live charts)
npm run nano:lab:smoke    # lighter smoke config + live charts
npm run nano:lab:bench    # formal bench + live charts
```

Dashboard shows: SM util / mem controller / VRAM / power bars, util+VRAM sparklines,
per-CPU-core busy %, live AR vs BoN vs MAE table. Requires CUDA.

Outputs under `results/nano-lm/<name>-lab/`.

## Student + teacher matrix (phase 11)

Agenda: [docs/NANO-STUDENT-AGENDA.md](../docs/NANO-STUDENT-AGENDA.md)

```bash
npm run nano:matrix          # B0–B2 + B3/B4/H-SPEC + H-SEL/BON/MAE + H-SUP/INT
npm run nano:matrix:report   # kill/promote table → docs/results/nano-lm/
npm run nano:spec            # B3/B4/H-SPEC only (reuses B2 ckpts when present)
npm run nano:bal             # H-BAL Baldwin smoke (merge into matrix.json)
npm run nano:dec             # H-DEC evolve decode knobs vs B4
npm run nano:lam             # H-LAM Lamarckian write-back vs H-BAL
npm run nano:eli             # H-ELI strong elitism vs H-SEL
npm run nano:ent             # H-ENT dual-head entanglement vs B2
npm run nano:ann             # H-ANN anneal vs cosine KD
npm run nano:formal:hsel     # longer B2 vs H-SEL (8 prompts, 3 seeds)
npm run nano:formal:hsel:report
```

Teacher: TinyStories-33M (frozen). Student: ≤5M GPT-Neo-tiny.
Formal note: smoke H-SEL promote was reversed — see `docs/results/nano-lm/formal-hsel-vs-b2.md`.
H-SPEC smoke: KILL vs B3 (no tokens/s speedup) — see kill/promote matrix.
H-BAL smoke: KILL/hold vs B2 — see `docs/results/nano-lm/hbal-vs-b2.md`.
H-DEC smoke: PROMOTE vs B4 (tentative) — see `docs/results/nano-lm/hdec-vs-b4.md`.
H-LAM smoke: PROMOTE vs H-BAL (tentative) — see `docs/results/nano-lm/hlam-vs-hbal.md`.
H-ELI smoke: KILL/hold vs H-SEL — see `docs/results/nano-lm/heli-vs-hsel.md`.
H-ENT smoke: KILL (head collapse) — see `docs/results/nano-lm/hent-vs-b2.md`.
H-ANN smoke: PROMOTE vs KD-cos (tentative) — see `docs/results/nano-lm/hann-vs-kdcos.md`.

## Commands

```bash
# Contract tests (no model download)
cd nano_lm && .venv/bin/pytest tests/ -q

# Smoke bench (downloads TinyStories-1M on first run)
python src/run_bench.py configs/smoke.json

# Aggregate
python src/aggregate.py --runs ../results/nano-lm/smoke/runs.jsonl \
  --out-md ../docs/results/nano-lm/smoke-summary.md
```

From repo root: `npm run nano:test`, `npm run nano:smoke`, `npm run nano:aggregate`, `npm run nano:lab`.

## Protocol

See [docs/NANO-LM-TRACK.md](../docs/NANO-LM-TRACK.md).
