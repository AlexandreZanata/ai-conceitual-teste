# Nano Wave W — close-out summary

> Public science report for Wave W (curated KB + domain PACK gates + efficiency).  
> Lab book: `.local/pesquisa.md`. Deploy: [RECIPES.md](RECIPES.md) · [champion-card.md](champion-card.md).

**Status: COMPLETE** · Wave X+: **COMPLETE** ([wave-x-summary.md](wave-x-summary.md)) · Wave Y: **ACTIVE** (cache + long ctx — `.local/pesquisa.md`).

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

## Wave X / Y (F4)

Wave X+ **COMPLETE** — full matrix: [wave-x-summary.md](wave-x-summary.md) (PFB family **PROMOTE**; QI/ABS **KILL** → [`archive/`](archive/)).  
**Wave Y ACTIVE** — [wave-y-summary.md](wave-y-summary.md) (PFB256/ROLL/SUMCACHE **PROMOTE**; STREAM **KILL**; next H-KVCACHE-Q). Corpus E1–E5: `CURATED-SOURCES.md` · [e5-eval-suites.md](e5-eval-suites.md).

## Commands (survivors)

```bash
npm run nano:curated
npm run nano:prog && npm run nano:formal:hprog
npm run nano:btc && npm run nano:formal:hbtc
npm run nano:eff && npm run nano:formal:heff
```
