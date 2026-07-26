# AGENTS.md — Nano generative LM (active)

> **Read this first** in any new agent session.

**Project:** Nano generative student (≤5M) under `nano_lm/` — speed, efficiency, curated KB.  
**Language:** 100% English for code, comments, commits, and agent technical output.  
**EvoGen C++ PoC:** frozen — [`docs/archive/evogen/`](docs/archive/evogen/README.md).

When rules conflict with existing code, **rules prevail** — unless the user explicitly overrides.

---

## What this repo is

| Is | Is not |
|----|--------|
| Nano causal LM research (tips + recipes + domain KB) | Generic ML framework / SaaS |
| Public curated programming + frontier corpora | Private scrape dump |
| STAG′ / EARLY / POOL + PACK efficiency stack | Unbounded model scale |

---

## Always load

1. `agent-rules/AGENT-CORE-PRINCIPLES.md`
2. `agent-rules/00-core/size-and-complexity-limits.md` — **80 / 200 / ≤10**
3. `docs/ARCHITECTURE.md` + `docs/GLOSSARY.md`
4. `docs/NANO-STUDENT-AGENDA.md` + `docs/results/nano-lm/champion-card.md` + `RECIPES.md`
5. `.local/pesquisa.md` (lab **NO-REOPEN** KILLs; Waves W–AF **COMPLETE + FROZEN**; **Wave AG OPEN** — [wave-ag-session.md](docs/results/nano-lm/wave-ag-session.md) · [af-freeze.md](docs/results/nano-lm/af-freeze.md) · [wave-af-summary.md](docs/results/nano-lm/wave-af-summary.md) · [paper-lab-wave-af.md](docs/results/nano-lm/paper-lab-wave-af.md) · [ae-freeze.md](docs/results/nano-lm/ae-freeze.md) · [wave-ae-summary.md](docs/results/nano-lm/wave-ae-summary.md) · [paper-lab-wave-ae.md](docs/results/nano-lm/paper-lab-wave-ae.md) · [ad-freeze.md](docs/results/nano-lm/ad-freeze.md) · [ac-freeze.md](docs/results/nano-lm/ac-freeze.md) · [ab-freeze.md](docs/results/nano-lm/ab-freeze.md))
6. `nano_lm/data/CURATED-SOURCES.md` before data work
7. Wave AG session: `.local/wave-ag/SESSION.md` · Wave AF: `.local/wave-af/SESSION.md` · Wave AE: `.local/wave-ae/SESSION.md` · Wave AD: `.local/wave-ad/SESSION.md` · Wave AC: `.local/wave-ac/SESSION.md` · Wave AB: `.local/wave-ab/SESSION.md` · Wave AA: `.local/wave-aa/SESSION.md` · Wave Z: `.local/wave-z/SESSION.md`

```bash
./agent-harness/rules-path.sh
./agent-harness/resolve-rules.sh <keywords>
npm run nano:test && npm run verify
```

---

## Delivery posture

- Survival PoC v1 **closed** → archive.  
- Nano Waves U–W **closed** (recipes frozen; XFER2 + MIXD purged).  
- Wave X+ **COMPLETE** — PFB family **PROMOTE**; QI/ABS **KILL** → [`wave-x-summary.md`](docs/results/nano-lm/wave-x-summary.md).  
- **Wave Y COMPLETE** — GPFB4-LONG **PROMOTE**; STREAM/KVCACHE-Q/GENCACHE **KILL**.  
- **Wave Z COMPLETE** — [wave-z-hitl.md](docs/results/nano-lm/wave-z-hitl.md) · **LAB-FREEZE** [lab-freeze.md](docs/results/nano-lm/lab-freeze.md).  
- **Wave AA COMPLETE + FROZEN** — [wave-aa-summary.md](docs/results/nano-lm/wave-aa-summary.md) · [aa-freeze.md](docs/results/nano-lm/aa-freeze.md) (`npm run nano:aa:freeze`).
- **Wave AB COMPLETE + FROZEN** — [wave-ab-summary.md](docs/results/nano-lm/wave-ab-summary.md) · [ab-freeze.md](docs/results/nano-lm/ab-freeze.md) · [paper-lab-wave-ab.md](docs/results/nano-lm/paper-lab-wave-ab.md) (`npm run nano:ab:freeze`).
- **Wave AC COMPLETE + FROZEN** — [wave-ac-summary.md](docs/results/nano-lm/wave-ac-summary.md) · [ac-freeze.md](docs/results/nano-lm/ac-freeze.md) · [paper-lab-wave-ac.md](docs/results/nano-lm/paper-lab-wave-ac.md) · [wave-ac-hitl.md](docs/results/nano-lm/wave-ac-hitl.md) (`npm run nano:ac:freeze`).
- **Wave AD COMPLETE + FROZEN** — [ad-freeze.md](docs/results/nano-lm/ad-freeze.md) · [wave-ad-summary.md](docs/results/nano-lm/wave-ad-summary.md) · [paper-lab-wave-ad.md](docs/results/nano-lm/paper-lab-wave-ad.md) · [wave-ad-hitl.md](docs/results/nano-lm/wave-ad-hitl.md) (`npm run nano:ad:freeze`).
- **Wave AE COMPLETE + FROZEN** — [wave-ae-summary.md](docs/results/nano-lm/wave-ae-summary.md) · [ae-freeze.md](docs/results/nano-lm/ae-freeze.md) · [paper-lab-wave-ae.md](docs/results/nano-lm/paper-lab-wave-ae.md) · [wave-ae-hitl.md](docs/results/nano-lm/wave-ae-hitl.md) (`npm run nano:ae:freeze`).
- **Wave AF COMPLETE + FROZEN** — [wave-af-summary.md](docs/results/nano-lm/wave-af-summary.md) · [af-freeze.md](docs/results/nano-lm/af-freeze.md) · [paper-lab-wave-af.md](docs/results/nano-lm/paper-lab-wave-af.md) · [wave-af-hitl.md](docs/results/nano-lm/wave-af-hitl.md) (`npm run nano:af:freeze`); ship claim = **AF packaged stack**.
- **Wave AG OPEN (research complete)** — [wave-ag-session.md](docs/results/nano-lm/wave-ag-session.md) · [wave-ag-summary.md](docs/results/nano-lm/wave-ag-summary.md) · [paper-lab-wave-ag.md](docs/results/nano-lm/paper-lab-wave-ag.md) · [wave-ag-hitl.md](docs/results/nano-lm/wave-ag-hitl.md) · formals ANTIFP…APPREAL (`npm run nano:ag:session` · … · `npm run nano:ag:hitl` · `npm run nano:ag:report`); next **AG8 AG-FREEZE**; ship claim remains **AF packaged stack**; no Wave AH invent without reopen.

---

## Quality gates (Lefthook)

Every commit: file ≤200, function ≤80, cyclomatic ≤10, lint 0/0, system 0 errors → `npm run verify`.

---

## Local workspace

`.local/` is gitignored. Public mirrors under `docs/`.  
Curated blobs under `nano_lm/data/curated/` are gitignored — regenerate with `npm run nano:curated`.
