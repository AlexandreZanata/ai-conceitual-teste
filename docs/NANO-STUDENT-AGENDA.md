# Nano Student + Teacher — Research Agenda

> Lab under `nano_lm/`. Caps: ≤80 / ≤200 / cyclo ≤10.  
> EvoGen survival: frozen [`archive/evogen/`](archive/evogen/README.md).

## Tips

**H-STAG′** (train; PRE3 via [TIPD](results/nano-lm/formal-htipd-vs-hstag.md)) · **H-EARLY** · **H-POOL**  
Parent control: live **H-STAG**.

## Recipes (faster / cheaper)

| Priority | Recipe | Notes |
|----------|--------|-------|
| 1 | **H-PACK** | Primary speed; elongated+OOD@128+howto+prog+btc; **not** ood_long |
| 2 | **H-TPACK** + **AMORT** | Steps / e2e n≥4 (tip = STAG′) |
| 3 | **H-QPACK** | Quality serve **in-harness only** (XFER KILL) |

Deploy: [H-DEPL](results/nano-lm/formal-hdepl-policy.md). Domain: [H-DOM](results/nano-lm/formal-hdom-howto.md) · [H-PROG](results/nano-lm/formal-hprog-programming.md) · [H-BTC](results/nano-lm/formal-hbtc-bitcoin.md).  
One-pager: [`RECIPES.md`](results/nano-lm/RECIPES.md).

## Wave W (COMPLETE)

**Mechanism:** curated public KB (programming + bitcoin/frontier) + PACK efficiency on new domains.  
Summary: [`wave-w-summary.md`](results/nano-lm/wave-w-summary.md).  
Data: [`nano_lm/data/CURATED-SOURCES.md`](../nano_lm/data/CURATED-SOURCES.md) · `npm run nano:curated`.  
Lab: `.local/pesquisa.md`. Card: [`champion-card.md`](results/nano-lm/champion-card.md).

| ID | Focus | Status |
|----|--------|--------|
| W0 CURATED | Download + manifest | DONE |
| W1 H-PROG | Programming domain PACK gate | smoke+formal **[PROMOTE](results/nano-lm/formal-hprog-programming.md)** |
| W2 H-BTC | Bitcoin/docs domain PACK gate | smoke+formal **[PROMOTE](results/nano-lm/formal-hbtc-bitcoin.md)** |
| W3 H-MIXD | STAG + curated train mix | formal **[KILL](results/nano-lm/hmixd-mix.md)** (tooling purged) |
| W4 H-EFF | PACK efficiency re-measure | smoke+formal **[PROMOTE](results/nano-lm/formal-heff-efficiency.md)** |

Wave X **PARKED** (new mechanism only). Phase E corpus growth **DONE** (E1–E3; see `CURATED-SOURCES.md`).

## Archived

KILL code purged (incl. XFER2, MIXD). [`results/nano-lm/archive/`](results/nano-lm/archive/).
