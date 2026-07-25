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
2. `agent-rules/00-core/size-and-complexity-limits.md` — **cyclomatic ≤10** (file/function line caps waived)
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
11. Nano champion stack frozen — **H-STAG** (train `seq_lo=6`, `n_stages=4`), **H-EARLY** / **H-POOL** (decode); parents H-CURL2←H-CURL←H-CUR / H-DECKL←H-DECK←H-DEC  
12. Dead hyp code purged (weight-evo + Waves A–H deepeners) — markdown in `docs/results/nano-lm/archive/`  
13. Wave I queue (faster/efficient new parents) — see `.local/pesquisa.md`
14. H-LAY layer early-exit — done (smoke **PROMOTE**; **formal PROMOTE** wall↓; GFLOPs tie)
15. H-AMP CUDA autocast bf16 — done (smoke **KILL** — quality < EARLY−ε; wall↑)
16. H-TIE tied+shared block under STAG — done (smoke **KILL** — quality < STAG−ε; params↓)
17. H-PRUN magnitude prune STAG + recovery — done (smoke **PROMOTE**; **formal PROMOTE** wall↓)
18. H-WIN local sliding-window attn — done (smoke **KILL** — quality < STAG−ε; FLOPs↓)
19. H-SHORT two-phase short draft — done (smoke **PROMOTE**; **formal PROMOTE** wall↓ tiny; GFLOPs tie)
20. H-SOFT offline soft-label cache — done (smoke **KILL** — equal lp; train ms/step↑)
21. H-BAT batched multi-prompt EARLY — done (smoke **PROMOTE**; **formal PROMOTE** tok/s↑; tip unchanged)
22. Wave J / H-TOP top-k soft-label cache — done (smoke+formal **PROMOTE** — ms/step↓ vs live STAG; lp↑)
23. Wave J / H-BUCKET length-banded BAT — done (smoke **KILL** — lp=BAT; tok/s↓ vs flat BAT)
24. Wave J / H-REP rep-penalty under EARLY — done (smoke **KILL** — no quality@wall win vs EARLY)
25. Wave J / H-ALT alternate full/shallow depth — done (smoke **KILL** — quality < EARLY−ε; wall/GFLOPs↓)
26. Wave J complete — backlog opened
27. H-FLASH SDPA backend on EARLY — done (smoke+formal **PROMOTE** — wall↓; lp=EARLY; tip unchanged)
28. H-KVSEL gated KV (`max_new` > thr) — done (smoke+formal **PROMOTE** — dual-budget wall↓; lp≈EARLY; tip unchanged)
29. H-DEPTH 1-layer STAG + PRUN recover — done (smoke+formal **PROMOTE** — wall↓; lp↑ vs tip; tip STAG unchanged)
30. H-MIX PRUN ckpt ⊕ LAY decode — done (smoke **PROTOCOL** — wall↓ vs PRUN; not a tip H-ID)
31. Wave K / H-TOPK top-k sweep — done (smoke **PROMOTE** / formal **KILL** — tip k=64 stands)
32. Wave K / H-FUSE FLASH⊕KVSEL — done (smoke **PROTOCOL** — wall < min(FLASH,KVSEL); not a tip)
33. Wave K / H-POOLB batched POOL — done (smoke+formal **PROMOTE** — tok/s↑; lp=serial; tip POOL unchanged)
34. Wave K / H-PIN pinned TOP H2D — done (smoke+formal **PROMOTE** — ms/step↓ vs TOP; lp=TOP)
35. Wave K / H-CHUNK chunked prefill under FLASH — done (smoke+formal **PROMOTE** — wall↓ vs FLASH; lp=EARLY; tip unchanged)
36. Wave L / H-Q4 int4 CUDA on DEPTH — done (smoke **PROMOTE** / formal **KILL** — quality < DEPTH−ε)
37. Wave L / H-CFUSE CHUNK⊕FUSE protocol — done (smoke **KILL** — wall ≥ min(CHUNK,FUSE); not a tip)
38. Wave L / H-CBAT chunked prefill under BAT — done (smoke+formal **PROMOTE** — tok/s↑; lp=BAT)
39. Wave L / H-CHB chunk_size sweep vs CHUNK — done (smoke+formal **PROMOTE** — B=256 wall↓)
40. Wave L / H-ASYNC cache∩PIN overlap — done (smoke **KILL** — e2e wall↑ vs PIN; lp tie)
41. Wave L focus queue complete (L6 skipped) — see `.local/pesquisa.md`
42. Wave M / H-CPOOLB chunked prefill under POOLB — done (smoke+formal **PROMOTE** — tok/s↑; lp=POOLB)
43. Wave M / H-CHBAT CHB B under CBAT — done (smoke+formal **PROMOTE** — tok/s↑; lp=CBAT)
44. Wave M / H-FUSEB FUSE under CHBAT batch — done (smoke+formal **PROMOTE** — tok/s↑ + wall↓; lp=CHBAT)
45. Wave M focus queue complete — see `.local/pesquisa.md`
46. Wave N / H-FCPOOLB FUSE under CPOOLB — done (smoke+formal **PROMOTE** — tok/s↑ + wall↓; lp=CPOOLB)
47. Wave N / H-LAYB LAY under FUSEB — done (smoke+formal **PROMOTE** — tok/s↑ + wall↓; lp=FUSEB)
48. Wave N / H-SHORTB SHORT under FUSEB — done (smoke **KILL** — lp change vs FUSEB; skip formal)
49. Wave N focus queue complete — see `.local/pesquisa.md`
50. Wave O / H-FLAYB LAY under FCPOOLB — done (smoke+formal **PROMOTE** — tok/s↑ + wall↓; lp=FCPOOLB)
51. Wave O / H-DEPTHB DEPTH_prun under LAYB — done (smoke **KILL** — |Δlp| > ε vs LAYB; skip formal)
52. Wave O / H-PINC torch.compile under PIN — done (smoke **KILL** — ms/step↑ vs PIN; skip formal)
53. Wave O focus queue complete — see `.local/pesquisa.md`
54. Wave P / H-PRUNB PRUN under LAYB — done (smoke **KILL** — |Δlp| > ε vs LAYB; skip formal)
55. Wave P / H-PRUNF PRUN under FLAYB — done (smoke **KILL** — |Δlp| > ε vs FLAYB; skip formal)
56. Wave P / H-GRAPH CUDA graph under LAYB — done (smoke+formal **PROMOTE** — wall↓; lp=LAYB)
57. Wave P focus queue complete — see `.local/pesquisa.md`
58. Wave Q / H-GRAPHF CUDA graph under FLAYB — done (smoke+formal **PROMOTE** — wall↓; lp=FLAYB)
59. Wave Q / H-GALL CUDA graph all budgets — done (smoke+formal **PROMOTE** — wall↓; lp=GRAPH)

**Research PoC v1** (survival-benchmark narrative): complete — see `docs/results/BENCHMARK-REPORT.md`.  
**Nano-LM side track:** `docs/NANO-LM-TRACK.md` + slim `docs/NANO-STUDENT-AGENDA.md` + [`champion-card.md`](docs/results/nano-lm/champion-card.md) + `docs/results/nano-lm/kill-promote-matrix.md` (KILL history in `archive/`).  
Private plan: `.local/SURVIVAL-GAME-PLAN.md`. Keep T1 unit/contract suite green.
**Next:** continue Wave Q or park — see `.local/pesquisa.md`

---

## Quality gates (Lefthook)

Every commit (local included): cyclomatic ≤10 (file/function line caps waived), lint 0/0, system 0 errors.

Extend size scanner to `.cpp`/`.hpp` **before** the first C++ sources are committed.

---

## Local workspace

`.local/` is gitignored. Public mirrors live under `docs/`.  
Every algorithm step must cite an official or plan-local reference URL/path in the phase `OFFICIAL-REFERENCE.md`.
