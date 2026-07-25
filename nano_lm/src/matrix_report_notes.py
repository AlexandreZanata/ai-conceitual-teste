"""Footer notes + gate blurbs for champion matrix markdown."""

GATES = [
    "H-SPEC gate: tokens/s > B3 and teacher_lp ≥ B3 − 0.05.",
    "H-DEC / H-DECK / H-DECKL / H-POOL / H-EARLY: decode tips (see formal docs).",
    "H-CUR / H-CURL / H-CURL2 / H-STAG: curriculum train (official = H-STAG lo=6, stages=4).",
    "H-FLOP: report tokens/s + est. GFLOPs with wall (instrumentation).",
    "Decode utils: LAY/LAYB/FLAYB/GRAPH/GRAPHF/GALL/GALLF/SHORT/FLASH/KVSEL/CHUNK/CHB/BAT/CBAT/CHBAT/FUSEB/POOLB/CPOOLB/FCPOOLB (tips unchanged).",
    "Train utils: PRUN/TOP/DEPTH/PIN/PRE/HALF (tip STAG/TOP/PIN/PRE unchanged).",
    "H-Q4 gate: lp ≥ DEPTH−ε and wall < DEPTH (formal KILL — quality cliff).",
    "H-ASYNC gate: lp ≥ PIN−ε and e2e_wall < PIN (smoke KILL — e2e↑).",
    "H-PINC gate: lp ≥ PIN−ε and ms/step < PIN (smoke KILL — compile tax).",
    "H-PRE gate: lp ≥ PIN−ε and ms/step < PIN (formal PROMOTE).",
    "H-HALF gate: lp ≥ PRE−ε and ms/step < PRE (formal PROMOTE).",
    "H-CPOOLB gate: lp ≥ POOLB−ε and tok/s > POOLB (formal PROMOTE).",
    "H-CHBAT gate: lp ≥ CBAT−ε and tok/s > CBAT (formal PROMOTE).",
    "H-FUSEB gate: lp ≥ CHBAT−ε and (tok/s > CHBAT or wall < CHBAT) (formal PROMOTE).",
    "H-FCPOOLB gate: lp ≥ CPOOLB−ε and (tok/s > CPOOLB or wall < CPOOLB) (formal PROMOTE).",
    "H-LAYB gate: lp ≥ FUSEB−ε and (tok/s > FUSEB or wall < FUSEB) (formal PROMOTE).",
    "H-FLAYB gate: lp ≥ FCPOOLB−ε and (tok/s > FCPOOLB or wall < FCPOOLB) (formal PROMOTE).",
    "H-GRAPH gate: lp ≥ LAYB−ε and wall < LAYB (formal PROMOTE).",
    "H-GRAPHF gate: lp ≥ FLAYB−ε and wall < FLAYB (formal PROMOTE).",
    "H-GALL gate: lp ≥ GRAPH−ε and wall < GRAPH (formal PROMOTE).",
    "H-GALLF gate: lp ≥ GRAPHF−ε and wall < GRAPHF (smoke KILL — wall↑).",
    "H-DEPTHB gate: lp ≥ LAYB−ε and (wall < LAYB or GFLOPs < LAYB) (smoke KILL — |Δlp|>ε).",
    "H-PRUNB gate: lp ≥ LAYB−ε and (wall < LAYB or GFLOPs < LAYB) (smoke KILL — |Δlp|>ε).",
    "H-PRUNF gate: lp ≥ FLAYB−ε and (wall < FLAYB or GFLOPs < FLAYB) (smoke KILL — |Δlp|>ε).",
    "H-SHORTB gate: lp ≥ FUSEB−ε and (tok/s > FUSEB or wall < FUSEB) (smoke KILL — lp cliff).",
    "H-MIX / H-FUSE / H-CFUSE: PROTOCOL only (not tip H-IDs); CFUSE smoke KILL.",
]

NOTES = [
    "## Notes",
    "- Focus stack: systems + batch + TOP/PIN + DEPTH. Archive: `docs/results/nano-lm/archive/`.",
    "- Official tips: **H-STAG** / **H-EARLY** / **H-POOL**.",
    "- H-TOPK / H-Q4 formal KILL; H-CFUSE / **H-ASYNC** / **H-SHORTB** / **H-DEPTHB** / "
    "**H-PINC** / **H-PRUNB** / **H-PRUNF** / **H-GALLF** smoke KILL; "
    "**H-CBAT** / **H-CHB** / **H-CPOOLB** / **H-CHBAT** / **H-FUSEB** / **H-FCPOOLB** / "
    "**H-LAYB** / **H-FLAYB** / **H-GRAPH** / **H-GRAPHF** / **H-GALL** / **H-PRE** / "
    "**H-HALF** formal PROMOTE; **H-GALLF** smoke KILL. "
    "Wave Q Q5 done (`.local/pesquisa.md`).",
    "- Smoke budgets are tentative; formal claims need 3 seeds + fit≠eval.",
    "- Agenda: `docs/NANO-STUDENT-AGENDA.md`.",
]
