# Champion card — tip-stack protocol (parked)

> Nano-LM compose tree closed (SYS→JOINT→CACHE→CAP all smoke **KILL**).  
> Official stack keeps **separate axes** — do not paste tips into one free-lunch H-ID.

## Protocol

| Step | Action | Tip | Formal evidence |
|------|--------|-----|-----------------|
| 1. Train | Curriculum KD | **H-STAG** (`seq_lo=6`, `n_stages=4`) | [formal-hstag-vs-hcurl2.md](formal-hstag-vs-hcurl2.md) |
| 1′. Train util | Mag prune + recovery | **H-PRUN** (util) | [formal-hprun-vs-hstag.md](formal-hprun-vs-hstag.md) |
| 1″. Train util | Top-k soft-label cache | **H-TOP** (util) | [formal-htop-vs-hstag.md](formal-htop-vs-hstag.md) |
| 1‴. Train util | 1-layer STAG + PRUN recover | **H-DEPTH** (util) | [formal-hdepth-vs-hstag.md](formal-hdepth-vs-hstag.md) |
| 2a. Decode (speed) | Early-exit gene | **H-EARLY** | [formal-hearly-vs-b4.md](formal-hearly-vs-b4.md) |
| 2a′. Decode util | Layer early-exit | **H-LAY** (util) | [formal-hlay-vs-hearly.md](formal-hlay-vs-hearly.md) |
| 2a″. Decode util | Short draft stop | **H-SHORT** (util) | [formal-hshort-vs-hearly.md](formal-hshort-vs-hearly.md) |
| 2a‴. Decode util | SDPA attention backend | **H-FLASH** (util) | [formal-hflash-vs-hearly.md](formal-hflash-vs-hearly.md) |
| 2a⁗. Decode util | Gated KV (`max_new` > thr) | **H-KVSEL** (util) | [formal-hkvsel-vs-hearly.md](formal-hkvsel-vs-hearly.md) |
| 2b. Decode (quality@wall) | Warm-start BoN gene | **H-POOL** (`top_k=1`) | [formal-hpool-vs-hdeckl.md](formal-hpool-vs-hdeckl.md) |
| 2c. Eval throughput | Batched multi-prompt | **H-BAT** (util) | [formal-hbat-vs-hearly.md](formal-hbat-vs-hearly.md) |
| — | Protocol stack (not a tip) | **H-MIX** = PRUN ckpt ⊕ LAY | [hmix-protocol.md](hmix-protocol.md) |
| — | Protocol stack (not a tip) | **H-FUSE** = FLASH ⊕ KVSEL | [hfuse-protocol.md](hfuse-protocol.md) |

Parents kept for lineage: **H-CURL2** (`seq_lo=6`, `n_stages=3`) ← **H-CURL** ← **H-CUR** (train), **H-DECKL ← H-DECK ← H-DEC** (decode).

## Formal scoreboard (claim table)

| ID | Axis | teacher_lp | wall_ms | Status |
|----|------|------------|---------|--------|
| B2 | train ctrl | −14.65 | ~70 | gate |
| B4 | decode ctrl | −14.49 | ~80 | gate |
| H-CURL | train parent | −13.36 | — | prior tip (lo=8) |
| H-CURL2 | train parent | −13.34 | — | prior tip (lo=6, stages=3) |
| **H-STAG** | train | **−13.28** | — | official train (lo=6, stages=4) |
| **H-EARLY** | decode | **−11.83** | **65** | official fast decode |
| **H-POOL** | decode | **−11.69** | **70** | official quality decode |

Decode efficiency also reports **tokens/s + est. GFLOPs** (`npm run nano:flop` → [hflop-instrumentation.md](hflop-instrumentation.md)); wall alone can mislead (EARLY smoke: wall↓, GFLOPs↑).

Smoke numbers never enter this table. Full KILL history: [`archive/`](archive/).

## Commands

```bash
npm run nano:stag && npm run nano:stag:report
npm run nano:early && npm run nano:early:report
npm run nano:pool && npm run nano:pool:report
npm run nano:bat && npm run nano:bat:report
npm run nano:flop && npm run nano:flop:report
npm run nano:formal:hstag && npm run nano:formal:hstag:report
npm run nano:formal:hprun && npm run nano:formal:hprun:report
npm run nano:formal:hearly && npm run nano:formal:hearly:report
npm run nano:formal:hlay && npm run nano:formal:hlay:report
npm run nano:formal:hshort && npm run nano:formal:hshort:report
npm run nano:formal:hpool && npm run nano:formal:hpool:report
npm run nano:formal:hbat && npm run nano:formal:hbat:report
npm run nano:formal:htop && npm run nano:formal:htop:report
npm run nano:topk && npm run nano:topk:report
npm run nano:formal:htopk && npm run nano:formal:htopk:report
npm run nano:formal:hflash && npm run nano:formal:hflash:report
npm run nano:formal:hkvsel && npm run nano:formal:hkvsel:report
npm run nano:formal:hdepth && npm run nano:formal:hdepth:report
npm run nano:mix && npm run nano:mix:report
npm run nano:fuse && npm run nano:fuse:report
```

## Closed compose branch (do not reopen without new parent)

| ID | Result | Lesson |
|----|--------|--------|
| H-SYS | smoke KILL | Tip paste is not free lunch |
| H-JOINT | smoke KILL | Joint train∪decode ≤ CURL default |
| H-CACHE | smoke KILL | Global KV raises wall on ≤5M student |
| H-CAP | smoke KILL | Hard length caps cut wall but quality < POOL−ε |

## Park status

**PARKED** (tips). Utils through Wave J + post-J complete.  
**Wave K ACTIVE** — **H-FUSE** smoke **PROTOCOL** ([hfuse-protocol.md](hfuse-protocol.md)); next **H-POOLB**.  
**H-TOPK** formal **KILL** ([formal-htopk-vs-htop.md](formal-htopk-vs-htop.md)).  
**H-MIX** remains PROTOCOL-only ([hmix-protocol.md](hmix-protocol.md)).

Agenda: [`docs/NANO-STUDENT-AGENDA.md`](../../NANO-STUDENT-AGENDA.md).  
Matrix: [`kill-promote-matrix.md`](kill-promote-matrix.md).
