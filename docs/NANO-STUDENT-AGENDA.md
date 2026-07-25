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

## Wave W (COMPLETE) → Wave X (ACTIVE)

**W mechanism:** curated KB + PACK on prog/btc + EFF. Summary: [`wave-w-summary.md`](results/nano-lm/wave-w-summary.md).  
**X mechanism:** dual teacher (story + **tiny code LM**) · long context · RAG/QT · quantum-*inspired* context · genetic context knobs · absurd sandbox. Lab: `.local/pesquisa.md`.

| ID | Focus | Status |
|----|--------|--------|
| W0 CURATED | Download + manifest | DONE |
| W1 H-PROG | Programming domain PACK gate | smoke+formal **[PROMOTE](results/nano-lm/formal-hprog-programming.md)** |
| W2 H-BTC | Bitcoin/docs domain PACK gate | smoke+formal **[PROMOTE](results/nano-lm/formal-hbtc-bitcoin.md)** |
| W3 H-MIXD | STAG + curated train mix | formal **[KILL](results/nano-lm/archive/hmixd-mix.md)** (tooling purged) |
| W4 H-EFF | PACK efficiency re-measure | smoke+formal **[PROMOTE](results/nano-lm/formal-heff-efficiency.md)** |

Wave X+ **ACTIVE** — **H-TCHR** / **H-QT** / **H-GENC** / **H-ABS-PFB** **[PROMOTE](results/nano-lm/formal-htchr-code-teacher.md)** / **[PROMOTE](results/nano-lm/formal-hqt-quantize.md)** / **[PROMOTE](results/nano-lm/formal-hgenc-genome.md)** / **[PROMOTE](results/nano-lm/formal-hpfb-pfb.md)** · long-L/RAG/CKD/Q*/GENQ/DIST/Q-SLOT/INTERF/ABS-REV/ANNEAL/SPIRAL/GROVER/TUNNEL/BELL/ORACLE1/DNA/DEBATE/HOLO/PHASE/ENTPOS/MEASURE/TELE/WIGNER/CHRONO/MIRROR/CBON/CSAFE **KILL** (see [`archive/`](results/nano-lm/archive/)) → **HOLD** / new H-ID (`.local/pesquisa.md`). Phase E corpus **DONE** ([e5-eval-suites.md](results/nano-lm/e5-eval-suites.md)).

## Archived

KILL code purged (incl. XFER2, MIXD). [`results/nano-lm/archive/`](results/nano-lm/archive/).
