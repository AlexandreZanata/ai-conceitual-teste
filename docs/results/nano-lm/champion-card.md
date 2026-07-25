# Champion card — tip-stack + official recipes

> Compose closed (**H-SYS** / **H-JOINT** / **H-CACHE** / **H-CAP** **KILL**).  
> Deploy one-pager: [RECIPES.md](RECIPES.md). Queue: `.local/pesquisa.md` (**Wave V**).

## Official tips

| Tip | Role | Formal |
|-----|------|--------|
| **H-STAG′** | Train (PRE3/RETIP) | [TIPD](formal-htipd-vs-hstag.md) · parent [H-STAG](formal-hstag-vs-hcurl2.md) |
| **H-EARLY** | Decode speed | [formal-hearly-vs-b4.md](formal-hearly-vs-b4.md) |
| **H-POOL** | Decode quality@wall | [formal-hpool-vs-hdeckl.md](formal-hpool-vs-hdeckl.md) |

## Official recipes (priority order)

| # | Recipe | Pack | Evidence |
|---|--------|------|----------|
| 1 | **Serve-fast** (primary) | **H-PACK** | [formal](formal-hpack-vs-hearly.md) · [XFER2](hxfer2-transfer.md) **KILL** ood_long · [BUD](formal-hbud-budget.md) · [DEPL](formal-hdepl-policy.md) |
| 2 | **Train-step / e2e** | **H-TPACK** + **AMORT** | [tpack](formal-htpack-vs-hstag.md) · [amort](formal-hamort-vs-hstag.md) · [TIPD](formal-htipd-vs-hstag.md) |
| 3 | **Serve-quality** (in-harness) | **H-QPACK** | [formal](formal-hqpack-vs-hpool.md) · OOD [XFER](hxfer-transfer.md) **KILL** · [DEPL](formal-hdepl-policy.md) |

## Tip scoreboard

| ID | teacher_lp | wall_ms | Status |
|----|------------|---------|--------|
| **H-STAG′** | **−12.49** | — | official train (TIPD) |
| H-STAG (parent) | −13.28 | — | control |
| **H-EARLY** | **−11.83** | **65** | official fast |
| **H-POOL** | **−11.69** | **70** | official quality |

## Commands

```bash
npm run nano:pack && npm run nano:formal:hpack
npm run nano:tpack && npm run nano:formal:htpack
npm run nano:amort && npm run nano:formal:hamort
npm run nano:tipd && npm run nano:formal:htipd
npm run nano:depl && npm run nano:formal:hdepl
npm run nano:qpack && npm run nano:formal:hqpack
npm run nano:bud && npm run nano:formal:hbud
npm run nano:xfer2 && npm run nano:xfer2:report
```

## Park status

**Wave V** — ~~DEPL~~ smoke+formal **PROMOTE** (policy ↔ BUD).  
Optional next: **H-DOM**.  
~~TIPD~~ `STAG_PRIME` · ~~XFER2~~ smoke **KILL** (ood_long).  
KILL history: [`archive/`](archive/). No new letter-packs.

Agenda: [`docs/NANO-STUDENT-AGENDA.md`](../../NANO-STUDENT-AGENDA.md).
