# Nano Student + Teacher — Research Agenda

> Lab under `nano_lm/`. Caps: ≤80 / ≤200 / cyclo ≤10.

## Tips

**H-STAG′** (train; PRE3 via [TIPD](results/nano-lm/formal-htipd-vs-hstag.md)) · **H-EARLY** · **H-POOL**  
Parent control: live **H-STAG**.

## Recipes (faster / cheaper)

| Priority | Recipe | Notes |
|----------|--------|-------|
| 1 | **H-PACK** | Primary speed; elongated+OOD@128+howto; **not** ood_long |
| 2 | **H-TPACK** + **AMORT** | Steps / e2e n≥4 (tip = STAG′) |
| 3 | **H-QPACK** | Quality serve **in-harness only** (XFER KILL) |

Deploy: [H-DEPL](results/nano-lm/formal-hdepl-policy.md). Domain: [H-DOM](results/nano-lm/formal-hdom-howto.md).  
One-pager: [`RECIPES.md`](results/nano-lm/RECIPES.md).

## Wave V

**COMPLETE** — XFER2 · TIPD · DEPL · DOM.  
Lab: `.local/pesquisa.md`. Card: [`champion-card.md`](results/nano-lm/champion-card.md).  
**Park** — new wave only with a fresh mechanism.

## Archived

KILL code purged (ETRAIN N=1, compose, …). [`archive/`](results/nano-lm/archive/).
