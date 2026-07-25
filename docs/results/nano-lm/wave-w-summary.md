# Nano Wave W — close-out summary

> Public science report for Wave W (curated KB + domain PACK gates + efficiency).  
> Lab book: `.local/pesquisa.md`. Deploy: [RECIPES.md](RECIPES.md) · [champion-card.md](champion-card.md).

**Status: COMPLETE** · Wave X: **ACTIVE** (H-RAG → H-QT — see `.local/pesquisa.md`).

## Mission

Ship a faster + more efficient ≤5M generative student with a **curated public** knowledge base skewed to programming and frontier (bitcoin / protocols), without reopening EvoGen or inventing new pack genes.

## Outcomes

| Phase | ID | Decision | Evidence |
|-------|-----|----------|----------|
| A / W0 | CURATED | **DONE** | [`CURATED-SOURCES.md`](../../nano_lm/data/CURATED-SOURCES.md) · `npm run nano:curated` |
| B1 | **H-PROG** | smoke+formal **PROMOTE** | [formal-hprog-programming.md](formal-hprog-programming.md) |
| B2 | **H-BTC** | smoke+formal **PROMOTE** | [formal-hbtc-bitcoin.md](formal-hbtc-bitcoin.md) |
| B3 | H-FRONT | **SKIPPED** | BTC covers frontier protocol English |
| C | **H-MIXD** | formal **KILL** | [archive/hmixd-mix.md](archive/hmixd-mix.md) · [formal](archive/formal-hmixd-mix.md) |
| D | **H-EFF** | smoke+formal **PROMOTE** | [formal-heff-efficiency.md](formal-heff-efficiency.md) |

## Kill / promote matrix (Wave W)

| ID | Gate | Result | Claim update |
|----|------|--------|--------------|
| H-PROG | PACK dual gate vs EARLY on prog @128 | **PROMOTE** | PACK tip gate holds on programming domain |
| H-BTC | PACK dual gate vs EARLY on btc @128 | **PROMOTE** | PACK tip gate holds on bitcoin domain |
| H-MIXD | story teacher_lp ≥ STAG−ε **and** prog PPL ↓ | **KILL** | **no train-mix** claim; story regress (−13.60 < −13.28−ε) despite prog PPL ↓ |
| H-EFF | quality floor + wall↓ or tok/s↑ vs Phase B SERVE | **PROMOTE** | PACK SERVE efficiency ↑ on prog+btc; recipe freeze; no new genes |

## Formal efficiency snapshot (H-EFF)

| Domain | SERVE wall_ms | Phase B | SERVE tok/s | Phase B |
|--------|---------------|---------|-------------|---------|
| prog | 3 | 4 | 2523 | 1957 |
| btc | 6 | 7 | 2837 | 2360 |

Fit≠eval genes; seeds [0,1,2]; `cpu_threads=14`. TPACK/AMORT remain story-train-only.

## Frozen after Wave W

- Tips: **H-STAG′** / **H-EARLY** / **H-POOL** (unchanged).
- Primary serve-fast: **H-PACK** (howto + prog + btc @128; **not** ood_long).
- Train: **H-TPACK** + **H-AMORT**; quality serve: **H-QPACK** in-harness only.
- DEPL: speed→PACK (incl. prog/btc); REJECT ood_long / QPACK-OOD.
- TinyStories remains the story teacher; no silent teacher swap.

## Tooling purge (F3)

**H-MIXD** runners purged after KILL (`nano:mixd*` removed) — same pattern as XFER2. Archive reports retained under [`archive/`](archive/).

## Wave X (F4)

**ACTIVE** after Wave W close-out. Lab queue: `.local/pesquisa.md` (H-TCHR/H-QT/H-GENC/H-ABS-PFB/H-ABS-QPFB **PROMOTE** → long-L/RAG/CKD/Q*/GENQ/DIST/Q-SLOT/INTERF/ABS-REV/ANNEAL/SPIRAL/GROVER/TUNNEL/BELL/ORACLE1/DNA/DEBATE/HOLO/PHASE/ENTPOS/MEASURE/TELE/WIGNER/CHRONO/MIRROR/CBON/CSAFE **KILL** → HOLD/new H-ID).
[H-TCHR](formal-htchr-code-teacher.md) wires `bigcode/tiny_starcoder_py` as frozen **code teacher**. [H-QT](formal-hqt-quantize.md) int8 weight-only serve **PROMOTE**. [H-GENC](formal-hgenc-genome.md) genetic serve genome under BUD **PROMOTE**. [H-ABS-PFB](formal-hpfb-pfb.md) parent-fallback story-floor BoN **PROMOTE**. [H-ABS-QPFB](formal-hqpfb-qpfb.md) PFB on QT-int8 **PROMOTE**. [H-RAG](archive/hrag-retrieve.md) / [H-CTX](archive/hctx-long-window.md) / [H-CKD](archive/hckd-code-kd.md) / [H-QCTX](archive/hqctx-born-attn.md) / [H-QCOMP](archive/hqcomp-shadow-kv.md) / [H-Q-QUBITKV](archive/hqubitkv-critical-kv.md) / [H-GENQ-ABS](archive/hgenq-amplitude.md) / [H-DIST](archive/hdist-distill.md) / [H-Q-SLOT](archive/hqslot-slots.md) / [H-Q-INTERF](archive/hqinterf-interference.md) / [H-ABS-REV](archive/habsrev-reverse.md) / [H-Q-ANNEAL](archive/hqanneal-anneal.md) / [H-ABS-SPIRAL](archive/habsspiral-spiral.md) / [H-Q-GROVER](archive/hqgrover-grover.md) / [H-Q-TUNNEL](archive/hqtunnel-tunnel.md) / [H-Q-BELL](archive/hqbell-bell.md) / [H-ABS-ORACLE1](archive/horacle1-oracle.md) / [H-ABS-DNA](archive/hdna-dna.md) / [H-ABS-DEBATE](archive/hdebate-debate.md) / [H-ABS-HOLO](archive/hholo-holo.md) / [H-ABS-PHASE](archive/hphase-phase.md) / [H-Q-ENTPOS](archive/hentpos-entpos.md) / [H-Q-MEASURE](archive/hmeasure-measure.md) / [H-Q-TELE](archive/htele-teleport.md) / [H-Q-WIGNER](archive/hwigner-wigner.md) / [H-ABS-CHRONO](archive/hchrono-chrono.md) / [H-ABS-MIRROR](archive/hmirror-mirror.md) / [H-ABS-CBON](archive/hcbon-cbon.md) / [H-ABS-CSAFE](archive/hcsafe-csafe.md) **KILL**. Default mechanism must be **new** (not another pack letter). Corpus E1–E5 landed — see `CURATED-SOURCES.md` and [e5-eval-suites.md](e5-eval-suites.md).

## Commands (survivors)

```bash
npm run nano:curated
npm run nano:prog && npm run nano:formal:hprog
npm run nano:btc && npm run nano:formal:hbtc
npm run nano:eff && npm run nano:formal:heff
```
