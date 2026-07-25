# Champion card — tip-stack + official recipes

> Compose closed (**H-SYS** / **H-JOINT** / **H-CACHE** / **H-CAP** **KILL**).  
> KILL history: [`archive/`](archive/). Queue: `.local/pesquisa.md` (**Wave U**).

## Official tips (parked)

| Tip | Role | Formal |
|-----|------|--------|
| **H-STAG** | Train | [formal-hstag-vs-hcurl2.md](formal-hstag-vs-hcurl2.md) |
| **H-EARLY** | Decode speed | [formal-hearly-vs-b4.md](formal-hearly-vs-b4.md) |
| **H-POOL** | Decode quality@wall | [formal-hpool-vs-hdeckl.md](formal-hpool-vs-hdeckl.md) |

## Official recipes (tip-relative packs)

| Recipe | Pack | vs tip | Evidence | Transfer | Budget | Retip |
|--------|------|--------|----------|----------|--------|-------|
| Serve-fast | **H-PACK** | EARLY | [formal-hpack-vs-hearly.md](formal-hpack-vs-hearly.md) | holds | SURVIVE | — |
| Serve-quality | **H-QPACK** | POOL | [formal-hqpack-vs-hpool.md](formal-hqpack-vs-hpool.md) | OOD KILL | SURVIVE | — |
| Train-step | **H-TPACK** | STAG (ms/step) | [formal-htpack-vs-hstag.md](formal-htpack-vs-hstag.md) | eval KILL | SURVIVE | **PROMOTE** ([hretip](formal-hretip-vs-hstag.md)) |

Also: **H-BPACK**. CBAT demoted. ETRAIN purged.  
**H-XFER** KILL · **H-BUD** PROMOTE · **H-RETIP** PROMOTE (tips not replaced).

## Tip scoreboard

| ID | teacher_lp | wall_ms | Status |
|----|------------|---------|--------|
| **H-STAG** | **−13.28** | — | official train |
| **H-EARLY** | **−11.83** | **65** | official fast |
| **H-POOL** | **−11.69** | **70** | official quality |

Report tok/s + GFLOPs (`npm run nano:flop`).

## Commands

```bash
npm run nano:formal:hstag && npm run nano:formal:hearly && npm run nano:formal:hpool
npm run nano:pack && npm run nano:formal:hpack
npm run nano:qpack && npm run nano:formal:hqpack
npm run nano:tpack && npm run nano:formal:htpack
npm run nano:bud && npm run nano:formal:hbud
npm run nano:retip && npm run nano:formal:hretip
npm run nano:xfer && npm run nano:xfer:report
npm run nano:pareto && npm run nano:flop
```

## Park status

**PARKED** tips + Wave T packs.  
**Wave U:** XFER KILL · BUD PROMOTE · RETIP PROMOTE; next **H-AMORT** (optional) or park.  
No more letter-packs without a new mechanism.

Agenda: [`docs/NANO-STUDENT-AGENDA.md`](../../NANO-STUDENT-AGENDA.md).
