"""Footer notes + gate blurbs for champion matrix markdown."""

GATES = [
    "H-SPEC gate: tokens/s > B3 and teacher_lp ≥ B3 − 0.05.",
    "H-DEC / H-DECK / H-DECKL / H-POOL / H-EARLY: decode tips (see formal docs).",
    "H-CUR / H-CURL / H-CURL2 / H-STAG: curriculum train (official = H-STAG lo=6, stages=4).",
    "H-FLOP: report tokens/s + est. GFLOPs with wall (instrumentation).",
    "Decode utils: H-LAY / H-SHORT / H-FLASH / H-KVSEL / H-BAT / H-POOLB (tips unchanged).",
    "Train utils: H-PRUN / H-TOP / H-DEPTH / H-PIN (tip STAG/TOP unchanged).",
    "H-MIX: PROTOCOL only (PRUN⊕LAY; not a tip H-ID).",
    "H-FUSE: PROTOCOL iff lp ≥ EARLY−ε and wall < min(FLASH,KVSEL) (not a tip).",
    "H-TOPK gate: some k≠64 with lp ≥ tip−ε and ms/step < tip (formal KILL; tip k=64 stands).",
    "H-POOLB gate: |Δlp| ≤ ε vs serial POOL and tok/s > serial (formal PROMOTE).",
    "H-PIN gate: lp ≥ TOP−ε and ms/step < TOP (pinned H2D; formal PROMOTE).",
]

NOTES = [
    "## Notes",
    "- Champion stack only. Purged H-ID history: `docs/results/nano-lm/archive/`.",
    "- Official: **H-STAG** train / **H-EARLY** speed / **H-POOL** quality@wall.",
    "- Utils: LAY, SHORT, FLASH, KVSEL, BAT, POOLB, PRUN, TOP, DEPTH, PIN, FLOP.",
    "- Wave K: **H-PIN** formal **PROMOTE**; next **H-CHUNK** (`.local/pesquisa.md`).",
    "- Smoke budgets are tentative; formal claims need 3 seeds + fit≠eval.",
    "- Agenda: `docs/NANO-STUDENT-AGENDA.md`.",
]
