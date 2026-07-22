# AGENTS.md — EvoGen

> **Read this first** in any new agent session.

**Project:** EvoGen (repo folder may still be named `ai-conceitual-teste`)  
**Language:** 100% English for code, comments, commits, and agent technical output.  
**Product plan (PT):** `docs/plano-conceitual-evogen.md` — read for research intent; implement against English docs below.

When rules conflict with existing code, **rules prevail** — unless the user explicitly overrides.

---

## What this repo is

| Is | Is not |
|----|--------|
| Research PoC combining genetic + direct + selection learning | Generic ML framework |
| Single C++ binary + light web observation UI | Microservice / SaaS product |
| Experimentally comparable A/B/C conditions | Production recommender |

---

## Always load

1. `agent-rules/AGENT-CORE-PRINCIPLES.md`
2. `agent-rules/00-core/size-and-complexity-limits.md` — **80 / 200 / ≤10**
3. `docs/ARCHITECTURE.md` + `docs/GLOSSARY.md`
4. Active `.local/phases/*/README.md` + `OFFICIAL-REFERENCE.md` + `TASKS.md`
5. `docs/EXPERIMENTAL-DESIGN.md` before changing experiment semantics

Cursor: `.cursor/rules/*.mdc` applies automatically.

```bash
./agent-harness/rules-path.sh
./agent-harness/resolve-rules.sh <keywords>
npm run verify
```

---

## Delivery order (non-negotiable)

1. Docs / checklist (phase 02) — done  
2. Core evolutionary CLI (phase 03) — done  
3. DirectLearner + function approx (phase 04) — done  
4. Embedded web metrics (phase 05) — done  
5. Survival game arena (phase 06) — **next**  
6. Learning technique matrix (phase 07)  
7. Timed learning benchmarks (phase 08)  
8. Benchmark report (phase 09)

Private plan: `.local/SURVIVAL-GAME-PLAN.md`. Keep T1 unit/contract suite green while building the arena.

---

## Quality gates (Lefthook)

Every commit (local included): file ≤200, function ≤80, cyclomatic ≤10, lint 0/0, system 0 errors.

Extend size scanner to `.cpp`/`.hpp` **before** the first C++ sources are committed.

---

## Local workspace

`.local/` is gitignored. Public mirrors live under `docs/`.  
Every algorithm step must cite an official or plan-local reference URL/path in the phase `OFFICIAL-REFERENCE.md`.
