# Champion card — tip-stack protocol (parked)

> Nano-LM compose tree closed (SYS→JOINT→CACHE→CAP all smoke **KILL**).  
> Official stack keeps **separate axes** — do not paste tips into one free-lunch H-ID.

## Protocol

| Step | Action | Tip | Formal evidence |
|------|--------|-----|-----------------|
| 1. Train | Curriculum KD | **H-CURL2** (`seq_lo=6`, `n_stages=3`) | [formal-hcurl2-vs-hcurl.md](formal-hcurl2-vs-hcurl.md) |
| 2a. Decode (speed) | Early-exit gene | **H-EARLY** | [formal-hearly-vs-b4.md](formal-hearly-vs-b4.md) |
| 2b. Decode (quality@wall) | Warm-start BoN gene | **H-POOL** (`top_k=1`) | [formal-hpool-vs-hdeckl.md](formal-hpool-vs-hdeckl.md) |

Parents kept for lineage: **H-CURL** (`seq_lo=8`) ← **H-CUR** (train), **H-DECKL ← H-DECK ← H-DEC** (decode).

## Formal scoreboard (claim table)

| ID | Axis | teacher_lp | wall_ms | Status |
|----|------|------------|---------|--------|
| B2 | train ctrl | −14.65 | ~70 | gate |
| B4 | decode ctrl | −14.49 | ~80 | gate |
| H-CURL | train parent | −13.36 | — | prior tip (lo=8) |
| **H-CURL2** | train | **−13.34** | — | official train (lo=6) |
| **H-EARLY** | decode | **−11.83** | **65** | official fast decode |
| **H-POOL** | decode | **−11.69** | **70** | official quality decode |

Smoke numbers never enter this table. Full KILL history: [`archive/`](archive/).

## Commands

```bash
npm run nano:curl2 && npm run nano:curl2:report
npm run nano:early && npm run nano:early:report
npm run nano:pool && npm run nano:pool:report
npm run nano:formal:curl2 && npm run nano:formal:curl2:report
npm run nano:formal:hearly && npm run nano:formal:hearly:report
npm run nano:formal:hpool && npm run nano:formal:hpool:report
```

## Closed compose branch (do not reopen without new parent)

| ID | Result | Lesson |
|----|--------|--------|
| H-SYS | smoke KILL | Tip paste is not free lunch |
| H-JOINT | smoke KILL | Joint train∪decode ≤ CURL default |
| H-CACHE | smoke KILL | KV cache raises wall on ≤5M student |
| H-CAP | smoke KILL | Hard length caps cut wall but quality < POOL−ε |

## Park status

**PARKED.** Deepen CURL2 / EARLY / POOL separately if needed. No new compose H-ID until a formal-PROMOTE parent outside this tree.

Agenda: [`docs/NANO-STUDENT-AGENDA.md`](../../NANO-STUDENT-AGENDA.md).  
Matrix: [`kill-promote-matrix.md`](kill-promote-matrix.md).
