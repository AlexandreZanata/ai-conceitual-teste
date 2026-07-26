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
5. `.local/pesquisa.md` (lab **NO-REOPEN** KILLs; Waves W–**AJ** **COMPLETE + FROZEN**; **Wave AK OPEN** — AK0 [SESSION](docs/results/nano-lm/wave-ak-session.md) · AK1 [H-GENTRUE HOLD](docs/results/nano-lm/formal-hgentrue-gentrue.md) · AK2 [H-CTXMORE PROMOTE](docs/results/nano-lm/formal-hctxmore-ctxmore.md) · AK3 [H-SMARTMORE PROMOTE](docs/results/nano-lm/formal-hsmartmore-smartmore.md) · AJ0 [SESSION](docs/results/nano-lm/wave-aj-session.md) · AJ7 [AJ-REPORT](docs/results/nano-lm/wave-aj-summary.md) · AJ8 [AJ-FREEZE](docs/results/nano-lm/aj-freeze.md) · [formal-hajfreeze-aj-freeze.md](docs/results/nano-lm/formal-hajfreeze-aj-freeze.md) — [ai-freeze.md](docs/results/nano-lm/ai-freeze.md) · [formal-haifreeze-ai-freeze.md](docs/results/nano-lm/formal-haifreeze-ai-freeze.md) · [wave-ai-summary.md](docs/results/nano-lm/wave-ai-summary.md) · [paper-lab-wave-ai.md](docs/results/nano-lm/paper-lab-wave-ai.md) · [wave-ai-hitl.md](docs/results/nano-lm/wave-ai-hitl.md) · [ah-freeze.md](docs/results/nano-lm/ah-freeze.md) · [ag-freeze.md](docs/results/nano-lm/ag-freeze.md) · [af-freeze.md](docs/results/nano-lm/af-freeze.md) · [ae-freeze.md](docs/results/nano-lm/ae-freeze.md) · [ad-freeze.md](docs/results/nano-lm/ad-freeze.md) · [ac-freeze.md](docs/results/nano-lm/ac-freeze.md) · [ab-freeze.md](docs/results/nano-lm/ab-freeze.md))
6. `nano_lm/data/CURATED-SOURCES.md` before data work
7. Wave AK session: `.local/wave-ak/SESSION.md` · Wave AJ: `.local/wave-aj/SESSION.md` · Wave AI: `.local/wave-ai/SESSION.md` · Wave AH: `.local/wave-ah/SESSION.md` · Wave AG: `.local/wave-ag/SESSION.md` · Wave AF: `.local/wave-af/SESSION.md` · Wave AE: `.local/wave-ae/SESSION.md` · Wave AD: `.local/wave-ad/SESSION.md` · Wave AC: `.local/wave-ac/SESSION.md` · Wave AB: `.local/wave-ab/SESSION.md` · Wave AA: `.local/wave-aa/SESSION.md` · Wave Z: `.local/wave-z/SESSION.md`

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
- **Wave AG COMPLETE + FROZEN** — [wave-ag-session.md](docs/results/nano-lm/wave-ag-session.md) · [wave-ag-summary.md](docs/results/nano-lm/wave-ag-summary.md) · [paper-lab-wave-ag.md](docs/results/nano-lm/paper-lab-wave-ag.md) · [wave-ag-hitl.md](docs/results/nano-lm/wave-ag-hitl.md) · [ag-freeze.md](docs/results/nano-lm/ag-freeze.md) · [formal-hagfreeze-ag-freeze.md](docs/results/nano-lm/formal-hagfreeze-ag-freeze.md) (`npm run nano:ag:freeze`); ship claim remains **AF packaged stack**.
- **Wave AH COMPLETE + FROZEN** — [wave-ah-session.md](docs/results/nano-lm/wave-ah-session.md) · [wave-ah-summary.md](docs/results/nano-lm/wave-ah-summary.md) · [paper-lab-wave-ah.md](docs/results/nano-lm/paper-lab-wave-ah.md) · [wave-ah-hitl.md](docs/results/nano-lm/wave-ah-hitl.md) · [ah-freeze.md](docs/results/nano-lm/ah-freeze.md) · [formal-hahfreeze-ah-freeze.md](docs/results/nano-lm/formal-hahfreeze-ah-freeze.md) (`npm run nano:ah:freeze`); ship claim remains **AF packaged stack**.
- **Wave AI COMPLETE + FROZEN** — [wave-ai-session.md](docs/results/nano-lm/wave-ai-session.md) · [wave-ai-summary.md](docs/results/nano-lm/wave-ai-summary.md) · [paper-lab-wave-ai.md](docs/results/nano-lm/paper-lab-wave-ai.md) · [wave-ai-hitl.md](docs/results/nano-lm/wave-ai-hitl.md) · [ai-freeze.md](docs/results/nano-lm/ai-freeze.md) · [formal-haifreeze-ai-freeze.md](docs/results/nano-lm/formal-haifreeze-ai-freeze.md) (`npm run nano:ai:freeze`); ship claim remains **AF packaged stack**; ≤5M stays; Wave AJ reopened via lab-book §6.
- **Wave AJ COMPLETE + FROZEN** — AJ0 [SESSION PROMOTE](docs/results/nano-lm/wave-aj-session.md) (`npm run nano:aj:session`); AJ1 [H-GENPEAK PROMOTE](docs/results/nano-lm/formal-hgenpeak-genpeak.md) (`npm run nano:genpeak`); AJ2 [H-CTXPEAK PROMOTE](docs/results/nano-lm/formal-hctxpeak-ctxpeak.md) (`npm run nano:ctxpeak`); AJ3 [H-SMARTPEAK PROMOTE](docs/results/nano-lm/formal-hsmartpeak-smartpeak.md) (`npm run nano:smartpeak`); AJ4 [H-FASTPEAK PROMOTE](docs/results/nano-lm/formal-hfastpeak-fastpeak.md) (`npm run nano:fastpeak`); AJ5 [H-APPPEAK PROMOTE](docs/results/nano-lm/formal-happpeak-apppeak.md) (`npm run nano:apppeak`); AJ6 [AJ-HITL-10 PROMOTE](docs/results/nano-lm/wave-aj-hitl.md) (`npm run nano:aj:hitl`); AJ7 [AJ-REPORT PROMOTE](docs/results/nano-lm/wave-aj-summary.md) (`npm run nano:aj:report`); AJ8 [AJ-FREEZE PROMOTE](docs/results/nano-lm/aj-freeze.md) (`npm run nano:aj:freeze`); ship claim remains **AF packaged stack**; ≤5M stays; Wave AK reopened via lab-book.
- **Wave AK OPEN** — AK0 [SESSION PROMOTE](docs/results/nano-lm/wave-ak-session.md) (`npm run nano:ak:session`); AK1 [H-GENTRUE HOLD](docs/results/nano-lm/formal-hgentrue-gentrue.md) (`npm run nano:gentrue`); AK2 [H-CTXMORE PROMOTE](docs/results/nano-lm/formal-hctxmore-ctxmore.md) (`npm run nano:ctxmore`); AK3 [H-SMARTMORE PROMOTE](docs/results/nano-lm/formal-hsmartmore-smartmore.md) (`npm run nano:smartmore`); next **AK4 H-FASTMORE**; ship claim remains **AF packaged stack**; ≤5M stays; do not invent Wave AL.

---

## Quality gates (Lefthook)

Every commit: file ≤200, function ≤80, cyclomatic ≤10, lint 0/0, system 0 errors → `npm run verify`.

---

## Local workspace

`.local/` is gitignored. Public mirrors under `docs/`.  
Curated blobs under `nano_lm/data/curated/` are gitignored — regenerate with `npm run nano:curated`.
