# Nano student — kill / promote matrix (champions)

Source: `results/nano-lm/student-matrix/matrix.json`
Wall clock (matrix): 154.6s

Primary metric: teacher mean log-prob of student completions.
Full historical rows: `docs/results/nano-lm/archive/`.
H-SPEC gate: tokens/s > B3 and teacher_lp ≥ B3 − 0.05.
H-DEC / H-DECK / H-DECKL / H-POOL / H-EARLY: decode tips (see formal docs).
H-CUR / H-CURL / H-CURL2 / H-STAG: curriculum train (official = H-STAG lo=6, stages=4).
H-FLOP: report tokens/s + est. GFLOPs with wall (instrumentation).
H-LAY gate: lp ≥ EARLY−ε and (wall < EARLY or est_gflops < EARLY) (layer skip).

| family | mean teacher_lp | Δ vs B2 | mean wall_ms | tok/s | n | decision |
|--------|-----------------|---------|--------------|-------|---|-----------|
| B0 | -16.9633 | +0.1285 | 74 | — | 3 | control |
| B1 | -17.3335 | -0.2417 | 41 | — | 3 | control |
| B2 | -17.0918 | — | 86 | — | 3 | BASELINE (claim gate) |
| B3 | -17.0918 | +0.0000 | 72 | 679.9 | 3 | decode control (AR) |
| B4 | -17.0202 | +0.0716 | 55 | 585.9 | 3 | decode control (BoN) |
| H-SPEC | -1.3358 | +15.7560 | 239 | 134.1 | 3 | KILL (no speedup vs B3) |
| H-DEC | -16.9235 | +0.1683 | — | — | 3 | PROMOTE (beats fixed BoN/B4) |
| H-DECK | -16.4637 | +0.6281 | — | — | 3 | PROMOTE (quality@budget vs H-DEC) |
| H-CUR | -17.0133 | +0.0785 | 47 | — | 3 | PROMOTE (beats B2) |

## Notes
- Champion stack only. Purged H-ID history: `docs/results/nano-lm/archive/`.
- Official train tip: **H-STAG** (`formal-hstag-vs-hcurl2.md`).
- Official decode: **H-EARLY** (speed) / **H-POOL** (quality@wall).
- Waves A–H deepeners purged from code; see archive + `.local/pesquisa.md`.
- H-LAY smoke: `docs/results/nano-lm/hlay-vs-hearly.md` (PROMOTE wall↓; GFLOPs tie; formal deferred).
- Smoke budgets are tentative; formal claims need 3 seeds + fit≠eval.
- Agenda: `docs/NANO-STUDENT-AGENDA.md`.
