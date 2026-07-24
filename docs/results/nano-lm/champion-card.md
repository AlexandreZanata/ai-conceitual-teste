# Champion card — tip-stack protocol (parked)

> Nano-LM compose tree closed (SYS→JOINT→CACHE→CAP all smoke **KILL**).  
> Official stack keeps **separate axes** — do not paste tips into one free-lunch H-ID.

## Protocol

| Step | Action | Tip | Formal evidence |
|------|--------|-----|-----------------|
| 1. Train | Curriculum KD | **H-STAG** (`seq_lo=6`, `n_stages=4`) | [formal-hstag-vs-hcurl2.md](formal-hstag-vs-hcurl2.md) |
| 2a. Decode (speed) | Early-exit gene | **H-EARLY** | [formal-hearly-vs-b4.md](formal-hearly-vs-b4.md) |
| 2a′. Decode util | Layer early-exit | **H-LAY** (util) | [formal-hlay-vs-hearly.md](formal-hlay-vs-hearly.md) |
| 2b. Decode (quality@wall) | Warm-start BoN gene | **H-POOL** (`top_k=1`) | [formal-hpool-vs-hdeckl.md](formal-hpool-vs-hdeckl.md) |
| 2c. Eval throughput | Batched multi-prompt | **H-BAT** (util) | [formal-hbat-vs-hearly.md](formal-hbat-vs-hearly.md) |

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
npm run nano:formal:hearly && npm run nano:formal:hearly:report
npm run nano:formal:hlay && npm run nano:formal:hlay:report
npm run nano:formal:hpool && npm run nano:formal:hpool:report
npm run nano:formal:hbat && npm run nano:formal:hbat:report
```

## Closed compose branch (do not reopen without new parent)

| ID | Result | Lesson |
|----|--------|--------|
| H-SYS | smoke KILL | Tip paste is not free lunch |
| H-JOINT | smoke KILL | Joint train∪decode ≤ CURL default |
| H-CACHE | smoke KILL | KV cache raises wall on ≤5M student |
| H-CAP | smoke KILL | Hard length caps cut wall but quality < POOL−ε |

## Park status

**PARKED** on Waves A–H. **Wave I complete.** Formal deepeners: **H-BAT** / **H-LAY** PROMOTE (utils; tip EARLY unchanged). Next: formal PRUN/SHORT or Wave J (`.local/pesquisa.md`).

Agenda: [`docs/NANO-STUDENT-AGENDA.md`](../../NANO-STUDENT-AGENDA.md).  
Matrix: [`kill-promote-matrix.md`](kill-promote-matrix.md).
