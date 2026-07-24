"""Footer notes + gate blurbs for champion matrix markdown."""

GATES = [
    "H-SPEC gate: tokens/s > B3 and teacher_lp ≥ B3 − 0.05.",
    "H-DEC / H-DECK / H-DECKL / H-POOL / H-EARLY: decode tips (see formal docs).",
    "H-CUR / H-CURL / H-CURL2 / H-STAG: curriculum train (official = H-STAG lo=6, stages=4).",
    "H-FLOP: report tokens/s + est. GFLOPs with wall (instrumentation).",
    "H-LAY gate: lp ≥ EARLY−ε and (wall < EARLY or est_gflops < EARLY) (layer skip).",
]

NOTES = [
    "## Notes",
    "- Champion stack only. Purged H-ID history: `docs/results/nano-lm/archive/`.",
    "- Official train tip: **H-STAG** (`formal-hstag-vs-hcurl2.md`).",
    "- Official decode: **H-EARLY** (speed) / **H-POOL** (quality@wall).",
    "- Waves A–H deepeners purged from code; see archive + `.local/pesquisa.md`.",
    "- H-LAY smoke: `docs/results/nano-lm/hlay-vs-hearly.md` (PROMOTE wall↓; GFLOPs tie; formal deferred).",
    "- Smoke budgets are tentative; formal claims need 3 seeds + fit≠eval.",
    "- Agenda: `docs/NANO-STUDENT-AGENDA.md`.",
]
