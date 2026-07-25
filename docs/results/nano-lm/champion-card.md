# Champion card — tip-stack protocol (parked tips)

> Compose tree closed (**H-SYS** / **H-JOINT** / **H-CACHE** / **H-CAP** all **KILL**). Tips on **separate axes**.  
> KILL history: [`archive/`](archive/). Lab queue: `.local/pesquisa.md` (**Wave T**).

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
| Systems | FLASH → CHUNK → **CHB**; KVSEL; GRAPH → GRAPHF; **GALL**; **SERVE** (min-wall); **SROUTE**/ROUTE (Pareto); **PACK** (both vs EARLY) |
| Batch speed | **SKIP** + **LAYB** via **BPACK** (BAT→SKIP→LAYB; CBAT demoted) |
| Batch quality | **FLAYB** via **QPACK** (POOLB→…→FLAYB; + GRAPHF) |
| Protocol | MIX / FUSE / PARETO / PACK / BPACK / **QPACK** (**not** tips) |

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
npm run nano:skip && npm run nano:formal:hskip
npm run nano:pack && npm run nano:formal:hpack
npm run nano:bpack && npm run nano:formal:hbpack
npm run nano:qpack && npm run nano:formal:hqpack
npm run nano:chb && npm run nano:layb && npm run nano:gall
npm run nano:flayb && npm run nano:graphf
npm run nano:mix && npm run nano:fuse
```

## Park status

**PARKED** (tips).  
**Wave T FOCUS** — **T1 H-QPACK** smoke+formal **PROMOTE**; next **H-TPACK**.  
**H-QPACK** smoke+formal **PROMOTE** ([formal-hqpack-vs-hpool.md](formal-hqpack-vs-hpool.md) — FLAYB beats POOL; lp≈POOL; wall↓ tok/s↑).  
**H-BPACK** smoke+formal **PROMOTE** ([formal-hbpack-vs-hearly.md](formal-hbpack-vs-hearly.md) — SKIP+LAYB both beat EARLY; GFLOPs=EARLY).  
**H-PACK** / **H-SKIP** / **H-SROUTE** prior PROMOTEs stand.  
KILL families purged from `nano_lm/` (ASYNC/PINC/GALLF/DEPTHA/B/PRUNB/F/SHORTB/CFUSE/Q4).

Agenda: [`docs/NANO-STUDENT-AGENDA.md`](../../NANO-STUDENT-AGENDA.md).  
Matrix: [`kill-promote-matrix.md`](kill-promote-matrix.md).
