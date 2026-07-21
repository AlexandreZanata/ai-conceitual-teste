# New Project Checklist — EvoGen

> Complete **before writing the first line of product C++**.
> Mirrors `agent-rules/AGENT-CORE-PRINCIPLES.md`.
> If any item is blank, the agent **must ask** — never assume.

---

## Architecture and domain

- [x] **Layers defined** — [ARCHITECTURE.md](ARCHITECTURE.md)
- [x] **Entities and aggregates** — Genome, Agent, Population, Environment, Experiment
- [x] **Value Objects** — Genome fields; Generation metrics; InheritanceMode; ExperimentCondition
- [x] **Business rules** — three mechanisms + A/B/C conditions in [EXPERIMENTAL-DESIGN.md](EXPERIMENTAL-DESIGN.md)
- [x] **State machines** — Experiment: `configured → running → paused → stopped` (API lifecycle)
- [ ] **Access roles** — N/A for local research PoC (single-user localhost); confirm before any network bind beyond localhost
- [x] **Domain events** — `GenerationCompleted`, `ExperimentStarted`, `ExperimentPaused` (WS/API)
- [x] **Use cases** — `docs/use-cases/UC-001` … `UC-003`
- [x] **API contract** — [API-CONTRACT.md](API-CONTRACT.md)
- [x] **Glossary** — [GLOSSARY.md](GLOSSARY.md)

---

## Security (OWASP)

- [x] **OWASP Top 10:2025** — localhost research tool; bind localhost by default; no auth in v1; revisit if exposed
- [x] **Agentic 2026** — coding agents use harness; runtime EvoGen agents are not tool-using LLMs (N/A for product agents)

---

## Agent harness

- [x] **Harness installed** — `agent-rules/`, `agent-harness/`, `.cursor/rules/`
- [x] **AGENTS.md** — project entry
- [x] **Ponytail (static)** — present
- [x] **Lefthook gates** — `npm run verify`

---

## Testing (contract-first)

- [x] **Policy read** — `agent-rules/04-testing/contract-first-tests.md`
- [x] **Unit tests** — Domain operators (Catch2; phase 03)
- [x] **Integration tests** — CLI one-generation + config load (phase 03)
- [ ] **E2E tests** — UC-003 when web exists
- [ ] **CI** — build + tests + quality on PR
- [x] **No mirror tests** — assert from experimental contract / golden vectors

---

## Research docs

- [x] Conceptual plan — [plano-conceitual-evogen.md](plano-conceitual-evogen.md)
- [x] Experimental design — [EXPERIMENTAL-DESIGN.md](EXPERIMENTAL-DESIGN.md)
- [x] Research questions — [RESEARCH-QUESTIONS.md](RESEARCH-QUESTIONS.md)
- [x] Experiment config stubs — `experiments/config_{A,B,C}_*.json`

---

## Sign-off

| Role | Name | Date |
|------|------|------|
| Product / domain | _(owner)_ | |
| Tech lead | _(owner)_ | |

When architecture/glossary/API boxes above are accepted, **phase 03 (core CLI)** may begin. Web UI must wait until phase 03–04 pass.
