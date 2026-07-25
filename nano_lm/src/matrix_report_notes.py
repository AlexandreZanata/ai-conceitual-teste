"""Footer notes + gate blurbs for champion matrix markdown."""

GATES = [
    "H-SPEC gate: tokens/s > B3 and teacher_lp ≥ B3 − 0.05.",
    "H-DEC / H-DECK / H-DECKL / H-POOL / H-EARLY: decode tips (see formal docs).",
    "H-CUR / H-CURL / H-CURL2 / H-STAG: curriculum train (official = H-STAG lo=6, stages=4).",
    "H-FLOP: report tokens/s + est. GFLOPs with wall (instrumentation).",
    "Decode utils: LAY/SHORT/FLASH/KVSEL/CHUNK/CHB/BAT/CBAT/CHBAT/FUSEB/POOLB/CPOOLB (tips unchanged).",
    "Train utils: PRUN/TOP/DEPTH/PIN (tip STAG/TOP unchanged).",
    "H-Q4 gate: lp ≥ DEPTH−ε and wall < DEPTH (formal KILL — quality cliff).",
    "H-ASYNC gate: lp ≥ PIN−ε and e2e_wall < PIN (smoke KILL — e2e↑).",
    "H-CPOOLB gate: lp ≥ POOLB−ε and tok/s > POOLB (formal PROMOTE).",
    "H-CHBAT gate: lp ≥ CBAT−ε and tok/s > CBAT (formal PROMOTE).",
    "H-FUSEB gate: lp ≥ CHBAT−ε and (tok/s > CHBAT or wall < CHBAT) (formal PROMOTE).",
    "H-MIX / H-FUSE / H-CFUSE: PROTOCOL only (not tip H-IDs); CFUSE smoke KILL.",
]

NOTES = [
    "## Notes",
    "- Focus stack: systems + batch + TOP/PIN + DEPTH. Archive: `docs/results/nano-lm/archive/`.",
    "- Official tips: **H-STAG** / **H-EARLY** / **H-POOL**.",
    "- H-TOPK / H-Q4 formal KILL; H-CFUSE / **H-ASYNC** smoke KILL; "
    "**H-CBAT** / **H-CHB** / **H-CPOOLB** / **H-CHBAT** / **H-FUSEB** formal PROMOTE. "
    "Wave M complete (`.local/pesquisa.md`).",
    "- Smoke budgets are tentative; formal claims need 3 seeds + fit≠eval.",
    "- Agenda: `docs/NANO-STUDENT-AGENDA.md`.",
]
