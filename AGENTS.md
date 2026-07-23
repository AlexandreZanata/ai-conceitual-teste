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
5. Survival game arena (phase 06) — done  
6. Learning technique matrix (phase 07) — done  
7. Timed learning benchmarks (phase 08) — done  
8. Benchmark report (phase 09) — done  
9. Nano-LM track TinyStories AR vs BoN vs MAE (phase 10) — done (smoke)  
10. Nano student + teacher agenda / matrix (phase 11) — done (smoke matrix)  
11. H-SPEC speculative decode vs B3/B4 — done (smoke **KILL**, no speedup)
12. H-BAL Baldwin lifetime GD — done (smoke **KILL/hold**, ≤ B2)
13. H-DEC evolve decode knobs — done (smoke **PROMOTE** vs B4, tentative)
14. H-LAM Lamarckian write-back — done (smoke **PROMOTE** vs H-BAL, tentative)
15. H-ELI strong elitism — done (smoke **KILL/hold** vs H-SEL)
16. H-ENT dual-head entanglement — done (smoke **KILL**, head collapse)
17. H-ANN anneal vs cosine KD — done (smoke **PROMOTE** vs KD-cos, tentative)
18. H-FIT teacher_lp fitness — done (smoke **PROMOTE** vs H-SEL, tentative)
19. H-TOU tournament selection — done (smoke **KILL/hold** vs H-SEL)
20. H-XOV weight crossover — done (smoke **PROMOTE** vs H-SEL, tentative)
21. H-NIC fitness sharing — done (smoke **KILL/hold** vs H-SEL; diversity↑ but tie)
22. H-MUT adaptive mutate scale — done (smoke **KILL/hold** vs H-SEL)
23. H-RAN linear rank selection — done (smoke **KILL/hold** vs H-SEL)
24. H-AGE age-layered pops — done (smoke **KILL/hold** vs H-SEL)
25. H-MOR soft mortality — done (smoke **KILL/hold** vs H-SEL)

**Research PoC v1** (survival-benchmark narrative): complete — see `docs/results/BENCHMARK-REPORT.md`.  
**Nano-LM side track:** `docs/NANO-LM-TRACK.md` + `docs/NANO-STUDENT-AGENDA.md` + kill/promote `docs/results/nano-lm/kill-promote-matrix.md` + result notes under `docs/results/nano-lm/`.  
Private plan: `.local/SURVIVAL-GAME-PLAN.md`. Keep T1 unit/contract suite green.

---

## Quality gates (Lefthook)

Every commit (local included): file ≤200, function ≤80, cyclomatic ≤10, lint 0/0, system 0 errors.

Extend size scanner to `.cpp`/`.hpp` **before** the first C++ sources are committed.

---

## Local workspace

`.local/` is gitignored. Public mirrors live under `docs/`.  
Every algorithm step must cite an official or plan-local reference URL/path in the phase `OFFICIAL-REFERENCE.md`.
