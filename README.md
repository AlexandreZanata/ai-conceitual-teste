# Nano generative LM lab

Active research: **≤5M student** causal LM — faster, more efficient, expanding curated knowledge (programming + frontier).

EvoGen C++ survival PoC is **frozen** under [`docs/archive/evogen/`](docs/archive/evogen/README.md).

Agents: start at **[AGENTS.md](AGENTS.md)**. Lab book: `.local/pesquisa.md` (Wave W).

## Quick start (nano)

```bash
npm install
npx lefthook install
python3 -m venv nano_lm/.venv && nano_lm/.venv/bin/pip install -r nano_lm/requirements.txt
npm run nano:test
npm run nano:curated   # public bitcoin / programming / RFC corpora
npm run verify
```

Recipes: [`docs/results/nano-lm/RECIPES.md`](docs/results/nano-lm/RECIPES.md)  
Agenda: [`docs/NANO-STUDENT-AGENDA.md`](docs/NANO-STUDENT-AGENDA.md)  
Curated sources: [`nano_lm/data/CURATED-SOURCES.md`](nano_lm/data/CURATED-SOURCES.md)

## Docs map (active)

| Doc | Purpose |
|-----|---------|
| [docs/ARCHITECTURE.md](docs/ARCHITECTURE.md) | Nano stack |
| [docs/GLOSSARY.md](docs/GLOSSARY.md) | Nano terms |
| [docs/NANO-LM-TRACK.md](docs/NANO-LM-TRACK.md) | Track overview |
| [docs/QUALITY-GATES.md](docs/QUALITY-GATES.md) | Lefthook caps |
| [docs/archive/evogen/](docs/archive/evogen/README.md) | Frozen EvoGen PoC |

## Frozen EvoGen (repro only)

```bash
npm run build
./build/evogen --config experiments/config_A_only_genetic.json --generations 1
```

## Quality gates

Cyclomatic ≤10 · lint 0/0 · `npm run verify`.
