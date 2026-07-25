# Champion card — tip-stack + official recipes

> Compose closed (**H-SYS** / **H-JOINT** / **H-CACHE** / **H-CAP** **KILL**).  
> Deploy one-pager: [RECIPES.md](RECIPES.md). Queue: `.local/pesquisa.md` (**Wave V**).

## Official tips (parked until H-TIPD)

| Tip | Role | Formal |
|-----|------|--------|
| **H-STAG** | Train | [formal-hstag-vs-hcurl2.md](formal-hstag-vs-hcurl2.md) |
| **H-EARLY** | Decode speed | [formal-hearly-vs-b4.md](formal-hearly-vs-b4.md) |
| **H-POOL** | Decode quality@wall | [formal-hpool-vs-hdeckl.md](formal-hpool-vs-hdeckl.md) |

## Official recipes (priority order)

| # | Recipe | Pack | Evidence |
|---|--------|------|----------|
| 1 | **Serve-fast** (primary) | **H-PACK** | [formal](formal-hpack-vs-hearly.md) · transfer elongated+ood · [XFER2](hxfer2-transfer.md) **KILL** ood_long · [BUD](formal-hbud-budget.md) |
| 2 | **Train-step / e2e / capacity** | **H-TPACK** + **AMORT** + **RETIP** | [tpack](formal-htpack-vs-hstag.md) · [amort](formal-hamort-vs-hstag.md) · [retip](formal-hretip-vs-hstag.md) |
| 3 | **Serve-quality** (in-harness) | **H-QPACK** | [formal](formal-hqpack-vs-hpool.md) · OOD [XFER](hxfer-transfer.md) **KILL** |

## Tip scoreboard

| ID | teacher_lp | wall_ms | Status |
|----|------------|---------|--------|
| **H-STAG** | **−13.28** | — | official train |
| **H-EARLY** | **−11.83** | **65** | official fast |
| **H-POOL** | **−11.69** | **70** | official quality |

## Commands

```bash
npm run nano:pack && npm run nano:formal:hpack
npm run nano:tpack && npm run nano:formal:htpack
npm run nano:amort && npm run nano:formal:hamort
npm run nano:retip && npm run nano:formal:hretip
npm run nano:qpack && npm run nano:formal:hqpack
npm run nano:bud && npm run nano:formal:hbud
npm run nano:xfer && npm run nano:formal:hxfer
npm run nano:xfer2 && npm run nano:xfer2:report
```

## Park status

**PARKED** (tips until **H-TIPD**). **Wave V ACTIVE** — next **H-TIPD** (RETIP→tip?).  
~~H-XFER2~~ smoke **KILL** (PACK holds elongated+ood; fails ood_long; skip formal).  
Then **H-DEPL** (BUD policy).  
KILL history: [`archive/`](archive/). No new letter-packs.

Agenda: [`docs/NANO-STUDENT-AGENDA.md`](../../NANO-STUDENT-AGENDA.md).
