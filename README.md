# EvoGen

Lightweight research PoC: **genetic learning + direct response learning + natural selection** in C++, with a web observation UI.

Conceptual plan (PT): [docs/plano-conceitual-evogen.md](docs/plano-conceitual-evogen.md)  
Agents: start at **[AGENTS.md](AGENTS.md)**.

## Quick start (repo tooling)

```bash
npm install
npx lefthook install
npm run build
npm run test
npm run verify
./build/evogen --config experiments/config_A_only_genetic.json --generations 1
```

Phase 03–08 done (CLI + DirectLearner + web + arena + technique matrix + **timed benches**).  
**Next:** benchmark report — `.local/phases/09-benchmark-report/`.

## Docs map

| Doc | Purpose |
|-----|---------|
| [docs/plano-conceitual-evogen.md](docs/plano-conceitual-evogen.md) | Full conceptual research plan (PT) |
| [docs/ARCHITECTURE.md](docs/ARCHITECTURE.md) | Layers and components |
| [docs/GLOSSARY.md](docs/GLOSSARY.md) | Ubiquitous language |
| [docs/EXPERIMENTAL-DESIGN.md](docs/EXPERIMENTAL-DESIGN.md) | A/B/C protocol + metrics + TB-* |
| [docs/results/survival-benchmark-summary.md](docs/results/survival-benchmark-summary.md) | Phase 08 smoke aggregate |
| [docs/RESEARCH-QUESTIONS.md](docs/RESEARCH-QUESTIONS.md) | Open RQs |
| [docs/API-CONTRACT.md](docs/API-CONTRACT.md) | REST/WS contract (phase 05) |
| [docs/TECH-STACK.md](docs/TECH-STACK.md) | C++ / web choices |
| [docs/QUALITY-GATES.md](docs/QUALITY-GATES.md) | Lefthook caps |
| [docs/NEW-PROJECT-CHECKLIST.md](docs/NEW-PROJECT-CHECKLIST.md) | Pre-code gate |

## Experiment configs

- `experiments/config_A_only_genetic.json`
- `experiments/config_B_only_direct.json`
- `experiments/config_C_full_system.json`
- `experiments/config_survival_C_smoke.json` — Trait Forge Arena (T2)
- `experiments/survival/*.json` — R0 / A / B / C / C-L / A+ technique presets
- `experiments/survival/benches/TB-*.json` — timed budget benches (phase 08)

```bash
python3 scripts/run_survival_bench.py --bench TB-30 --technique R0 --technique C --seeds 2
python3 scripts/aggregate_survival_bench.py
```

## Quality gates

File ≤200 lines · function ≤80 · cyclomatic ≤10 · lint 0/0 · system 0 errors.
