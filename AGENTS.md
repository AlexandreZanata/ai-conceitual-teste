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
13. H-DEC evolve decode knobs — done (smoke **PROMOTE**; **formal PROMOTE** vs B4 Δ+2.43)
14. H-LAM Lamarckian write-back — done (smoke **PROMOTE**; **formal KILL** vs H-BAL Δ−0.12)
15. H-ELI strong elitism — done (smoke **KILL/hold** vs H-SEL)
16. H-ENT dual-head entanglement — done (smoke **KILL**, head collapse)
17. H-ANN anneal vs cosine KD — done (smoke **PROMOTE**; **formal PROMOTE** vs KD-cos Δ+0.15; still ≪ B2)
18. H-FIT teacher_lp fitness — done (smoke **PROMOTE**; **formal KILL** vs B2 — overfit + Δ−1.84)
19. H-TOU tournament selection — done (smoke **KILL/hold** vs H-SEL)
20. H-XOV weight crossover — done (smoke **PROMOTE**; **formal KILL** vs B2 Δ−1.65)
21. H-NIC fitness sharing — done (smoke **KILL/hold** vs H-SEL; diversity↑ but tie)
22. H-MUT adaptive mutate scale — done (smoke **KILL/hold** vs H-SEL)
23. H-RAN linear rank selection — done (smoke **KILL/hold** vs H-SEL)
24. H-AGE age-layered pops — done (smoke **KILL/hold** vs H-SEL)
25. H-MOR soft mortality — done (smoke **KILL/hold** vs H-SEL)
26. H-SPE island speciation — done (smoke **KILL/hold** vs H-SEL)
27. H-SEX mate choice — done (smoke **KILL/hold** vs H-SEL)
28. H-ANTI anti-selection — done (smoke **KILL/hold** vs H-SEL)
29. H-TAX wealth tax — done (smoke **KILL/hold** vs H-SEL)
30. H-CAN LN cannibalism — done (smoke **KILL/hold** vs H-SEL; tie)
31. H-PAR parasite genome — done (smoke **KILL** — parasite dominates)
32. H-SYM obligate pair — done (smoke **PROMOTE**; **formal KILL** vs B2 Δ−1.66)
33. H-FOS fossil vault — done (smoke **KILL/hold** vs H-SEL; tie)
34. H-ZOM zombie reinject — done (smoke **KILL/hold** vs H-SEL)
35. H-LOTU underdog lottery — done (smoke **KILL/hold** vs H-SEL)
36. H-GLD Goldilocks fitness — done (smoke **KILL/hold** vs H-FIT; tie)
37. H-SEA seasonal fitness — done (smoke **KILL/hold** vs H-FIT)
38. H-RPS RPS niches — done (smoke **KILL** — niche collapse)
39. H-CAT catastrophe — done (smoke **KILL/hold** vs H-SEL)
40. H-HIB hibernation — done (smoke **KILL/hold** vs H-SEL)
41. H-SHO layer shock — done (smoke **PROMOTE**; **formal KILL** vs B2 Δ−1.86)
42. H-HOLD holdout fitness — done (smoke **PROMOTE**; **formal KILL** — overfit + reverse)
43. H-FXS FIT×XOV×SHO stack — done (smoke **KILL/hold** vs max(H-FIT,H-XOV))
44. H-LOFI low-fidelity rescore — done (smoke **KILL** — wall save but quality < H-FIT)
45. H-ENT2 dual-head TV floor — done (smoke **KILL** — collapsed again)
46. H-ENT3 max-TV + mix KD — done (smoke **KILL** — collapsed)
47. Formal H-HOLD vs B2 — done (**KILL** — overfit + reverse smoke; Δ−1.84)
48. Formal H-XOV vs B2 — done (**KILL** — reverse smoke; Δ−1.65; no collapse)
49. Formal H-FIT vs B2 — done (**KILL** — overfit + reverse smoke; Δ−1.84)
50. Formal H-SYM vs B2 — done (**KILL** — reverse smoke; Δ−1.66)
51. Formal H-DEC vs B4 — done (**PROMOTE confirmed** — Δ+2.43; no overfit)
52. Formal H-SHO vs B2 — done (**KILL** — reverse smoke; Δ−1.86)
53. Formal H-LAM vs H-BAL — done (**KILL** — reverse smoke; Δ−0.12; also ≤ B2)
54. H-LAT latency-aware decode vs B4 — done (smoke **KILL** — lp↑, no wall win)
55. H-DECK proxy+top-k decode — done (smoke **PROMOTE**; **formal PROMOTE** vs B4 Δ+2.53)
56. H-DECK2 top_k ablation — done (smoke **KILL**; **formal PROMOTE** — best k=1 Δ+0.25 vs k=2)
57. H-PROXY2 CE proxy vs self-lp — done (smoke **PROMOTE**; **formal KILL** — Δ−0.11 vs H-DECK)
58. H-CASC proxy→mid→full — done (smoke **PROMOTE**; **formal PROMOTE** vs B4 Δ+2.27)
59. H-BAND UCB1 gene arms — done (smoke **KILL** — ≤ H-DECK/H-CASC)
60. H-DECKL DECK+lat claim — done (smoke/formal **PROMOTE** — Pareto-dominates B4)
61. H-POOL cross-seed warm-start — done (smoke/formal **PROMOTE** Δ+0.04 vs cold H-DECKL)
62. H-PARE Pareto archive + knee claim — done (smoke/formal **PROMOTE** — Pareto-dominates B4 Δ+2.14)
63. H-LAT2 λ≥0.4 + n≤2 clamp — done (smoke/formal **PROMOTE** — Δ+2.39 vs B4 + wall win)
64. H-DECP per-prompt gene bank — done (smoke **PROMOTE**; **formal KILL** — ≤ GLOBAL on eval)
65. H-DECM elite gene mixture — done (smoke/formal **PROMOTE** — > H-LAT2 Δ+0.34, > B4 Δ+2.30)
66. H-DECQ quantized gene codes — done (smoke **PROMOTE**; **formal KILL** — ≤ H-DECM on eval)
67. H-DRAFT evolved speculative draft knobs — done (smoke **KILL** — no wall win vs B4)
68. H-BEAM evolved beam search — done (smoke **KILL** — no wall win vs B4; lp↑)
69. H-EARLY confidence early-exit — done (smoke/formal **PROMOTE** — Δ+2.66 vs B4 + wall win)
70. Formal H-ANN vs KD-cos — done (**PROMOTE confirmed** — Δ+0.15; both still ≪ B2)
71. H-STACK EARLY×DECM mixture claim — done (smoke **KILL** — ≤ max tip quality)
72. H-HEB local Hebbian MLP — done (smoke **KILL** — ≤ B2; stable)
73. H-EPI context LR/masks — done (smoke **KILL** — ≤ fixed LR / B2)
74. H-LOT sparse lottery ticket — done (smoke **PROMOTE**; **formal KILL** — quality cliff Δ−1.52)
75. H-HOP tiny Hopfield prior — done (smoke **PROMOTE**; **formal KILL** — Δ−0.40 vs B2)
76. H-BLK block-parallel decode — done (smoke **KILL** — no wall win vs B3; Δ−0.04)
77. H-DIF discrete diffusion nano — done (smoke **KILL** — ≤ B2 Δ−0.72; VRAM OK)
78. H-ADV weak discriminator + teacher judge — done (smoke **KILL** — ≤ B2; no collapse)
79. H-DEB dual student; teacher picks — done (smoke **PROMOTE**; **formal KILL** — Δ−0.01 vs B2)
80. H-ROUT confidence tip router — done (smoke **KILL** — ≤ max tip Δ−0.29; no dual)
81. H-ORAC teacher-oracle tip pick — done (smoke **KILL** — quality↑ but no dual wall)
82. H-TKD top-k sparse KD — done (smoke **PROMOTE**; **formal KILL** — Δ−2.03 vs B2)
83. H-REP repetition-penalty decode — done (smoke **KILL** — lp↑ vs B4; no wall win)
84. H-CLIP logit-clipped KD — done (smoke **KILL** — ≤ B2 Δ−0.34)

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
