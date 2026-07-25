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
5. `.local/pesquisa.md` (Wave W COMPLETE; Wave X ACTIVE — H-TCHR/H-QT PROMOTE; H-RAG/H-CTX/H-CKD KILL; next H-QCTX) before new H-IDs
6. `nano_lm/data/CURATED-SOURCES.md` before data work

```bash
./agent-harness/rules-path.sh
./agent-harness/resolve-rules.sh <keywords>
npm run nano:test && npm run verify
```

---

## Delivery posture

- Survival PoC v1 **closed** → archive.  
- Nano Waves U–W **closed** (recipes frozen; XFER2 + MIXD purged).  
- **Wave X ACTIVE** — H-TCHR/H-QT **PROMOTE**; H-RAG/H-CTX/H-CKD **KILL**; next H-QCTX — see `.local/pesquisa.md` + [`formal-htchr-code-teacher.md`](docs/results/nano-lm/formal-htchr-code-teacher.md) · [`formal-hqt-quantize.md`](docs/results/nano-lm/formal-hqt-quantize.md).

---

## Quality gates (Lefthook)

Every commit: file ≤200, function ≤80, cyclomatic ≤10, lint 0/0, system 0 errors → `npm run verify`.

---

## Local workspace

`.local/` is gitignored. Public mirrors under `docs/`.  
Curated blobs under `nano_lm/data/curated/` are gitignored — regenerate with `npm run nano:curated`.
