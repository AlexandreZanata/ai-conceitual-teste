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
11. Nano champion stack frozen — **H-CURL2** (train `seq_lo=6`), **H-EARLY** / **H-POOL** (decode); parents H-CURL←H-CUR / H-DECKL←H-DECK←H-DEC  
12. Dead hyp code purged — kill/non-champion markdown in `docs/results/nano-lm/archive/`
13. H-EAR2 widened early-exit gene — done (smoke **KILL** — quality < EARLY−ε)
14. H-BUD max_new + EARLY exit gene — done (smoke **KILL** — quality < EARLY−ε)
15. H-THIN thin CURL student + EARLY genes — done (smoke PROMOTE; formal **KILL** vs CURL Δ−0.33)
16. H-Q8 INT8 dynamic quant on CURL + EARLY — done (smoke **KILL** — no wall win vs tip)
17. H-EARS scheduled early-exit thr — done (smoke **KILL** — quality < EARLY−ε)
18. H-CURL2 fine seq_lo grid — done (smoke PROMOTE lo=12; formal **PROMOTE** lo=6 vs tip)
19. H-COMP torch.compile on EARLY tip — done (smoke **KILL** — no wall win; CUDAGraph overhead)
20. H-PROX CE-only fit proxy vs H-POOL — done (smoke **KILL** — claim quality < POOL−ε)
21. H-POOL2 tighter POOL search — done (smoke **KILL** — quality < POOL−ε; fit-fwd↓)
22. H-CURD teacher-NLL difficulty curriculum — done (smoke PROMOTE; formal **KILL** vs CURL2 Δ−1.16)
23. H-STEP early-stop KD under CURL2 — done (smoke **KILL** — worse lp than tip; steps↓)
24. H-ALAT (αT) KD α/T schedule under CURL2 — done (smoke **KILL** — ≤ tip Δ−0.23)
25. H-FLOP decode FLOP/tps instrumentation — done (smoke **PROMOTE** — metrics live; EARLY wall↓≠GFLOPs↓)
26. H-EARF FLOP-aware early-exit search — done (smoke **KILL** — no FLOP win vs EARLY tip)
27. H-EXIT earlier min_new + n=1 — done (smoke **KILL** — quality < EARLY−ε; GFLOPs↓)
28. H-MID mid min_new + tip warm-start — done (smoke PROMOTE; formal **KILL** vs EARLY Δ−0.51)

**Research PoC v1** (survival-benchmark narrative): complete — see `docs/results/BENCHMARK-REPORT.md`.  
**Nano-LM side track:** `docs/NANO-LM-TRACK.md` + slim `docs/NANO-STUDENT-AGENDA.md` + parked [`champion-card.md`](docs/results/nano-lm/champion-card.md) + `docs/results/nano-lm/kill-promote-matrix.md` (KILL history in `archive/`).  
Private plan: `.local/SURVIVAL-GAME-PLAN.md`. Keep T1 unit/contract suite green.

---

## Quality gates (Lefthook)

Every commit (local included): file ≤200, function ≤80, cyclomatic ≤10, lint 0/0, system 0 errors.

Extend size scanner to `.cpp`/`.hpp` **before** the first C++ sources are committed.

---

## Local workspace

`.local/` is gitignored. Public mirrors live under `docs/`.  
Every algorithm step must cite an official or plan-local reference URL/path in the phase `OFFICIAL-REFERENCE.md`.
