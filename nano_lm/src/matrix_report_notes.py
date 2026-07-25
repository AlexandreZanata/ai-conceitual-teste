"""Footer notes + gate blurbs for champion matrix markdown."""

GATES = [
    "H-SPEC gate: tokens/s > B3 and teacher_lp ≥ B3 − 0.05.",
    "Tips: H-STAG train / H-EARLY speed / H-POOL quality@wall.",
    "Serving utils: FLASH/CHUNK/CHB + LAYB/FLAYB + GRAPH/GRAPHF/GALL.",
    "Batch utils: BAT→CBAT→CHBAT→FUSEB; POOLB→CPOOLB→FCPOOLB.",
    "Train I/O: TOP→PIN→PRE→HALF→ADAMF→PRE2→PRE3.",
    "H-FLOP: wall + tok/s + est. GFLOPs.",
    "H-MIX / H-FUSE: PROTOCOL only (not tips).",
]

NOTES = [
    "## Notes",
    "- Focus winners only. KILL code purged; history: `docs/results/nano-lm/archive/`.",
    "- Wave R: R0 PRE3 PROMOTE; next SERVE/ETRAIN — `.local/pesquisa.md`.",
    "- Smoke budgets are tentative; formal = 3 seeds + fit≠eval.",
    "- Agenda: `docs/NANO-STUDENT-AGENDA.md`.",
]
