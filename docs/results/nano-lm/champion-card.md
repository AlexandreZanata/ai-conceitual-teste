# Champion card — tip-stack protocol (parked tips)

> Compose tree closed (**H-SYS** / **H-JOINT** / **H-CACHE** / **H-CAP** all **KILL**). Tips on **separate axes**.  
> KILL history: [`archive/`](archive/). Lab queue: `.local/pesquisa.md` (**Wave S**).

## Official tips

| Step | Tip | Formal |
|------|-----|--------|
| 1. Train | **H-STAG** (`seq_lo=6`, `n_stages=4`) | [formal-hstag-vs-hcurl2.md](formal-hstag-vs-hcurl2.md) |
| 2a. Decode speed | **H-EARLY** | [formal-hearly-vs-b4.md](formal-hearly-vs-b4.md) |
| 2b. Decode quality@wall | **H-POOL** (`top_k=1`) | [formal-hpool-vs-hdeckl.md](formal-hpool-vs-hdeckl.md) |

Parents: H-CURL2←H-CURL←H-CUR; H-DECKL←H-DECK←H-DEC.

## Winner utils (keep)

| Axis | Chain (tip unchanged) |
|------|------------------------|
| Train I/O | TOP → PIN → PRE → HALF → ADAMF → PRE2 → **PRE3** |
| Thin solo | PRUN / DEPTH (never under batch/ADAMF) |
| Systems | FLASH → CHUNK → **CHB**; KVSEL; GRAPH → GRAPHF; **GALL**; **SERVE** (min-wall=GALL); **SROUTE**/ROUTE (Pareto) |
| Batch speed | BAT → CBAT → CHBAT → FUSEB → **LAYB** (+ GRAPH/GALL) |
| Batch quality | POOLB → CPOOLB → FCPOOLB → **FLAYB** (+ GRAPHF) |
| Protocol | MIX = PRUN⊕LAY; FUSE = FLASH⊕KVSEL; **PARETO** = GFLOPs honesty audit (**not** tips) |

## Formal tip scoreboard

| ID | Axis | teacher_lp | wall_ms | Status |
|----|------|------------|---------|--------|
| B2 / B4 | gates | −14.65 / −14.49 | ~70 / ~80 | control |
| **H-STAG** | train | **−13.28** | — | official |
| **H-EARLY** | decode | **−11.83** | **65** | official fast |
| **H-POOL** | decode | **−11.69** | **70** | official quality |

Also report tok/s + est. GFLOPs (`npm run nano:flop`).

## Core commands

```bash
npm run nano:stag && npm run nano:formal:hstag
npm run nano:early && npm run nano:formal:hearly
npm run nano:pool && npm run nano:formal:hpool
npm run nano:pre2 && npm run nano:formal:hpre2
npm run nano:pre3 && npm run nano:formal:hpre3
npm run nano:etrain && npm run nano:formal:hetrain
npm run nano:serve && npm run nano:formal:hserve
npm run nano:route && npm run nano:formal:hroute
npm run nano:pareto && npm run nano:formal:hpareto
npm run nano:sroute && npm run nano:formal:hsroute
npm run nano:chb && npm run nano:layb && npm run nano:gall
npm run nano:flayb && npm run nano:graphf
npm run nano:mix && npm run nano:fuse
```

## Park status

**PARKED** (tips).  
**Wave S FOCUS** — **S0 H-SROUTE** smoke+formal **PROMOTE**; next **H-SKIP**.  
**H-SROUTE** smoke+formal **PROMOTE** ([formal-hsroute-vs-hserve.md](formal-hsroute-vs-hserve.md) — not dominated by SERVE; lp↑ tok/s↑; wall↑; SERVE keeps min-wall).  
**H-PARETO** smoke+formal **PROMOTE** ([formal-hpareto-audit.md](formal-hpareto-audit.md) — audit live; **H-CBAT** FLAG tok/s↑ GFLOPs↑).  
**H-ROUTE** smoke+formal **PROMOTE** ([formal-hroute-vs-arms.md](formal-hroute-vs-arms.md) — not dominated by GALL/GRAPHF; tok/s↑).  
**H-ETRAIN** smoke PROMOTE / formal **KILL** ([formal-hetrain-vs-hstag.md](formal-hetrain-vs-hstag.md) — e2e wall↑; cache tax).  
**H-SERVE** smoke+formal **PROMOTE** ([formal-hserve-vs-hearly.md](formal-hserve-vs-hearly.md) — recipe=`speed`/GALL; wall↓ tok/s↑; lp≈EARLY).  
**H-PRE3** smoke+formal **PROMOTE** ([formal-hpre3-vs-hpre2.md](formal-hpre3-vs-hpre2.md) — ms/step↓; lp=PRE2).  
KILL families purged from `nano_lm/` (ASYNC/PINC/GALLF/DEPTHA/B/PRUNB/F/SHORTB/CFUSE/Q4).

Agenda: [`docs/NANO-STUDENT-AGENDA.md`](../../NANO-STUDENT-AGENDA.md).  
Matrix: [`kill-promote-matrix.md`](kill-promote-matrix.md).
