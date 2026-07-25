"""Footer notes + gate blurbs for champion matrix markdown."""

GATES = [
    "H-SPEC gate: tokens/s > B3 and teacher_lp ≥ B3 − 0.05.",
    "H-DEC / H-DECK / H-DECKL / H-POOL / H-EARLY: decode tips (see formal docs).",
    "H-CUR / H-CURL / H-CURL2 / H-STAG: curriculum train (official = H-STAG lo=6, stages=4).",
    "H-FLOP: report tokens/s + est. GFLOPs with wall (instrumentation).",
    "Decode utils: LAY/SHORT/FLASH/KVSEL/CHUNK/BAT/POOLB (tips unchanged).",
    "Train utils: PRUN/TOP/DEPTH/PIN (tip STAG/TOP unchanged).",
    "H-Q4 gate: lp ≥ DEPTH−ε and wall < DEPTH (formal KILL — quality cliff).",
    "H-MIX / H-FUSE: PROTOCOL only (not tip H-IDs).",
]

NOTES = [
    "## Notes",
    "- Focus stack: systems + batch + TOP/PIN + DEPTH. Archive: `docs/results/nano-lm/archive/`.",
    "- Official tips: **H-STAG** / **H-EARLY** / **H-POOL**.",
    "- H-TOPK / H-Q4 formal KILL. Wave L next **H-CFUSE** (`.local/pesquisa.md`).",
    "- Smoke budgets are tentative; formal claims need 3 seeds + fit≠eval.",
    "- Agenda: `docs/NANO-STUDENT-AGENDA.md`.",
]
