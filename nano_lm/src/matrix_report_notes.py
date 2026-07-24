"""Footer notes + gate blurbs for champion matrix markdown."""

GATES = [
    "H-SPEC gate: tokens/s > B3 and teacher_lp ≥ B3 − 0.05.",
    "H-DEC / H-DECK / H-DECKL / H-POOL / H-EARLY: decode tips (see formal docs).",
    "H-CUR / H-CURL: curriculum train tips (official train = H-CURL seq_lo=8).",
    "H-EAR2 gate: lp ≥ EARLY−ε and wall < EARLY (widened early gene).",
    "H-BUD gate: not dominated by EARLY on (lp, wall); quality ≥ EARLY−ε.",
    "H-THIN gate: lp ≥ CURL−ε and wall < CURL on same EARLY decode.",
    "H-Q8 gate: lp ≥ CURL−ε and wall < CURL (INT8 dynamic on same EARLY).",
    "H-EARS gate: lp ≥ EARLY−ε and wall < EARLY (scheduled thr).",
]

NOTES = [
    "## Notes",
    "- Champion stack only. Purged H-ID history: `docs/results/nano-lm/archive/`.",
    "- H-EAR2 smoke: `docs/results/nano-lm/hear2-vs-hearly.md` (KILL — quality < EARLY−ε).",
    "- H-BUD smoke: `docs/results/nano-lm/hbud-vs-hearly.md` (KILL — quality < EARLY−ε).",
    "- H-THIN: smoke PROMOTE (`hthin-vs-hcurl.md`); formal **KILL** (`formal-hthin-vs-hcurl.md`).",
    "- H-Q8 smoke: `docs/results/nano-lm/hq8-vs-hcurl.md` (KILL — no wall win vs tip).",
    "- H-EARS smoke: `docs/results/nano-lm/hears-vs-hearly.md` (KILL — quality < EARLY−ε).",
    "- Smoke budgets are tentative; formal claims need 3 seeds + fit≠eval.",
    "- Agenda: `docs/NANO-STUDENT-AGENDA.md`.",
]
