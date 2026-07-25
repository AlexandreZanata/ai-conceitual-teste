# Official nano-LM recipes (frozen claims)

> Tip-stack: **H-STAG′** / **H-EARLY** / **H-POOL** (TIPD promoted train tip).  
> Packs are delivery envelopes — not tip replacements.  
> Lab: `.local/pesquisa.md` · Card: [champion-card.md](champion-card.md)

## Deploy one-liners

| Goal | Use | Do not claim |
|------|-----|----------------|
| **Fastest serve** | **H-PACK** (SERVE/SROUTE path) | OOD elongated to 256 ([XFER2](hxfer2-transfer.md) **KILL**) |
| **Quality@wall serve** | **H-QPACK** (FLAYB) | OOD / transfer (XFER **KILL**) |
| **Cheaper train steps** | **H-TPACK** (PRE3) | e2e without **H-AMORT** n≥4 |
| **Official train tip** | **H-STAG′** (PRE3 via [TIPD](formal-htipd-vs-hstag.md)) | Revert to live STAG without new formal |
| **E2E train wall** | **H-AMORT** (cache/n + PRE3) | ETRAIN N=1 (purged KILL) |

## Formal evidence

| Recipe | Doc | Wave U / V |
|--------|-----|------------|
| PACK | [formal-hpack-vs-hearly.md](formal-hpack-vs-hearly.md) | [XFER](hxfer-transfer.md) holds elongated+ood; [XFER2](hxfer2-transfer.md) **KILL** ood_long; [BUD](formal-hbud-budget.md) SURVIVE |
| QPACK | [formal-hqpack-vs-hpool.md](formal-hqpack-vs-hpool.md) | [XFER](hxfer-transfer.md) KILL; BUD SURVIVE |
| TPACK / tip | [formal-htpack-vs-hstag.md](formal-htpack-vs-hstag.md) | [TIPD](formal-htipd-vs-hstag.md) **PROMOTE** STAG′; [AMORT](formal-hamort-vs-hstag.md) |

## Policy (budget)

Under tip wall/GFLOPs ceilings ([BUD](formal-hbud-budget.md)): PACK + QPACK + TPACK **SURVIVE**.  
Prefer **PACK** when robustness matters (harness / elongated / OOD@128); QPACK only in-distribution / harness packs.
