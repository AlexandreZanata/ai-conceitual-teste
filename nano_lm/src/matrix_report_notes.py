"""Footer notes + gate blurbs for champion matrix markdown."""

GATES = [
    "H-SPEC gate: tokens/s > B3 and teacher_lp ≥ B3 − 0.05.",
    "H-DEC / H-DECK / H-DECKL / H-POOL / H-EARLY: decode tips (see formal docs).",
    "H-CUR / H-CURL / H-CURL2 / H-STAG: curriculum train (official = H-STAG lo=6, stages=4).",
    "H-FLOP: report tokens/s + est. GFLOPs with wall (instrumentation).",
    "H-LAY / H-SHORT / H-BAT: decode utils (wall or tok/s; tip EARLY unchanged).",
    "H-PRUN: train util (prune; tip STAG unchanged).",
    "H-TOP gate: lp ≥ STAG−ε and train ms/step < live STAG (top-k soft cache).",
    "H-BUCKET gate: |Δlp| ≤ ε vs H-BAT/serial and tok/s > H-BAT (length-banded pad).",
    "H-REP gate: lp > EARLY and wall ≤ EARLY (rep-penalty / no-repeat under tip).",
    "H-ALT gate: lp ≥ EARLY−ε and (wall < EARLY or gflops < EARLY) (alt full/shallow).",
]

NOTES = [
    "## Notes",
    "- Champion stack only. Purged H-ID history: `docs/results/nano-lm/archive/`.",
    "- Official: **H-STAG** train / **H-EARLY** speed / **H-POOL** quality@wall.",
    "- Utils kept: H-LAY, H-PRUN, H-SHORT, H-BAT, H-TOP, H-FLOP.",
    "- Wave I KILLs purged (WIN/TIE/AMP/SOFT). Wave J done: H-TOP PROMOTE; BUCKET+REP+ALT smoke KILL.",
    "- Smoke budgets are tentative; formal claims need 3 seeds + fit≠eval.",
    "- Agenda: `docs/NANO-STUDENT-AGENDA.md`.",
]
