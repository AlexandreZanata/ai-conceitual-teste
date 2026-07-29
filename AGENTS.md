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
5. `.local/pesquisa.md` — **lab source of truth** (wave status, anti-FP scoreboard, next actions)
6. `nano_lm/data/CURATED-SOURCES.md` before data work

```bash
./agent-harness/rules-path.sh
./agent-harness/resolve-rules.sh <keywords>
npm run nano:test && npm run verify
```

---

## Delivery posture

- Survival PoC v1 **closed** → `docs/archive/evogen/`.
- Waves W–**BF** **COMPLETE + FROZEN** — public mirrors under `docs/results/nano-lm/*-freeze.md`.
- **Wave BH ACTIVE** — BH0 [SESSION PROMOTE](docs/results/nano-lm/wave-bh-session.md) (`npm run nano:bh:session`) — IQ battery v0 plan · gold holes (Rust MISS · add truncation) · BA…BG/AZ hold · Track A++ util · gen stance **SKIP** (H-NANOGEN18); BH1 H-IQBAT PROMOTE (`npm run nano:iq-battery`); next BH2 H-GOLDFIX; ship remains **AF + AQ + AS trust + STRICT ablated DECODE**; NANOGEN6·7 HOLD · NANOGEN8…15 DEFER · NANOGEN16·17 SKIP; ≤5M stays.
- Active wave / reopen: **only** what `.local/pesquisa.md` says.
- Ship claim until gen PROMOTE: **AF + AQ + AS trust + STRICT ablated DECODE** — not unlabeled open chat · not TAC / mini-AGI unlocked.
- Generative north star: true_continue via real M1|M2|M3 — else SKIP/DEFER (no NANOGEN rename).

---

## Quality gates (Lefthook)

Every commit: file ≤200, function ≤80, cyclomatic ≤10, lint 0/0, system 0 errors → `npm run verify`.

---

## Local workspace

`.local/` is gitignored. Public mirrors under `docs/`.  
Curated blobs under `nano_lm/data/curated/` are gitignored — regenerate with `npm run nano:curated`.  
Heavy experiment dumps under `results/` are gitignored — regenerate with `npm run nano:*`.

## Cursor performance

See `.cursorignore` + `.cursorindexingignore`. After changing them: **Cursor: Resync Index**.
