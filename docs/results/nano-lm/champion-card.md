# Champion card — tip-stack + official recipes

> Compose closed (**H-SYS** / **H-JOINT** / **H-CACHE** / **H-CAP** **KILL**).  
> Deploy: [RECIPES.md](RECIPES.md). Lab: `.local/pesquisa.md` (**Wave X+** — code teacher · long ctx · QCTX/GEN).

## Official tips

| Tip | Role | Formal |
|-----|------|--------|
| **H-STAG′** | Train (PRE3/RETIP) | [TIPD](formal-htipd-vs-hstag.md) · parent [H-STAG](formal-hstag-vs-hcurl2.md) |
| **H-EARLY** | Decode speed | [formal-hearly-vs-b4.md](formal-hearly-vs-b4.md) |
| **H-POOL** | Decode quality@wall | [formal-hpool-vs-hdeckl.md](formal-hpool-vs-hdeckl.md) |

## Official recipes (priority order)

| # | Recipe | Pack | Evidence |
|---|--------|------|----------|
| 1 | **Serve-fast** (primary) | **H-PACK** | [formal](formal-hpack-vs-hearly.md) · [DOM](formal-hdom-howto.md) · [PROG](formal-hprog-programming.md) · [BTC](formal-hbtc-bitcoin.md) · [EFF](formal-heff-efficiency.md) · [BUD](formal-hbud-budget.md) · [DEPL](formal-hdepl-policy.md) · XFER2 KILL → [archive](archive/hxfer2-transfer.md) |
| 2 | **Train-step / e2e** | **H-TPACK** + **AMORT** | [tpack](formal-htpack-vs-hstag.md) · [amort](formal-hamort-vs-hstag.md) · [TIPD](formal-htipd-vs-hstag.md) |
| 3 | **Serve-quality** (in-harness) | **H-QPACK** | [formal](formal-hqpack-vs-hpool.md) · OOD [XFER](archive/hxfer-transfer.md) **KILL** · [DEPL](formal-hdepl-policy.md) |

## Tip scoreboard

| ID | teacher_lp | wall_ms | Status |
|----|------------|---------|--------|
| **H-STAG′** | **−12.49** | — | official train (TIPD) |
| H-STAG (parent) | −13.28 | — | control |
| **H-EARLY** | **−11.83** | **65** | official fast |
| **H-POOL** | **−11.69** | **70** | official quality |

## Commands

```bash
npm run nano:curated
npm run nano:pack && npm run nano:formal:hpack
npm run nano:tpack && npm run nano:formal:htpack
npm run nano:amort && npm run nano:formal:hamort
npm run nano:tipd && npm run nano:formal:htipd
npm run nano:depl && npm run nano:formal:hdepl
npm run nano:dom && npm run nano:formal:hdom
npm run nano:prog && npm run nano:formal:hprog
npm run nano:btc && npm run nano:formal:hbtc
npm run nano:eff && npm run nano:formal:heff
npm run nano:e5
npm run nano:tchr && npm run nano:formal:htchr
npm run nano:qt && npm run nano:formal:hqt
npm run nano:qpack && npm run nano:formal:hqpack
npm run nano:bud && npm run nano:formal:hbud
```

## Wave W / X+

Wave W **COMPLETE** — [wave-w-summary.md](wave-w-summary.md): **H-PROG** / **H-BTC** / **H-EFF** **PROMOTE**; **H-MIXD** **KILL** ([archive](archive/hmixd-mix.md)).  
**Wave X+ ACTIVE** — **H-TCHR** / **H-QT** smoke+formal **[PROMOTE](formal-htchr-code-teacher.md)** / **[PROMOTE](formal-hqt-quantize.md)** · **H-RAG** / **H-CTX** / **H-CKD** / **H-QCTX** / **H-QCOMP** **KILL** → [archive/hrag-retrieve.md](archive/hrag-retrieve.md) / [archive/hctx-long-window.md](archive/hctx-long-window.md) / [archive/hckd-code-kd.md](archive/hckd-code-kd.md) / [archive/hqctx-born-attn.md](archive/hqctx-born-attn.md) / [archive/hqcomp-shadow-kv.md](archive/hqcomp-shadow-kv.md) → **H-Q-QUBITKV** (`.local/pesquisa.md`).  
KILL history: [`archive/`](archive/).

Agenda: [`docs/NANO-STUDENT-AGENDA.md`](../../NANO-STUDENT-AGENDA.md).
