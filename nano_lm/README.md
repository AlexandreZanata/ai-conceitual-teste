# nano_lm — ≤5M generative student track

Active lab (EvoGen C++ frozen). Caps: ≤80 / ≤200 / cyclo ≤10.

## Stack

**H-STAG′** train · **H-EARLY** / **H-POOL** decode · **H-PACK** serve-fast · **H-TPACK**+**AMORT** train cost · **H-QPACK** in-harness quality.

Card: [`docs/results/nano-lm/champion-card.md`](../docs/results/nano-lm/champion-card.md) · Recipes: [`RECIPES.md`](../docs/results/nano-lm/RECIPES.md) · Lab: `.local/pesquisa.md` (**Wave X**: H-TCHR/H-QT/H-GENC **PROMOTE**; long-L/RAG/CKD/Q*/GENQ/DIST/Q-SLOT/INTERF/ABS-REV/ANNEAL/SPIRAL/GROVER/TUNNEL/BELL/ORACLE1/DNA/DEBATE/HOLO **KILL**; next H-ABS-PHASE).

## Setup

```bash
python3 -m venv nano_lm/.venv
nano_lm/.venv/bin/pip install -r nano_lm/requirements.txt
npm run nano:test
npm run nano:curated
```

## Survivors (repro)

```bash
npm run nano:pack && npm run nano:formal:hpack
npm run nano:prog && npm run nano:formal:hprog
npm run nano:btc && npm run nano:formal:hbtc
npm run nano:eff && npm run nano:formal:heff
npm run nano:tchr && npm run nano:formal:htchr
npm run nano:qt && npm run nano:formal:hqt
npm run nano:tpack && npm run nano:amort
```

KILL history: `docs/results/nano-lm/archive/` (XFER/MIXD/SPEC runners purged).
