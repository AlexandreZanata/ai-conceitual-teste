"""Footer notes + gate blurbs for champion matrix markdown."""

GATES = [
    "H-SPEC gate: tokens/s > B3 and teacher_lp ≥ B3 − 0.05.",
    "Tips: H-STAG train / H-EARLY speed / H-POOL quality@wall.",
    "Serving utils: FLASH/CHUNK/CHB + LAYB/FLAYB + GRAPH/GRAPHF/GALL + SERVE + ROUTE.",
    "Batch utils: BAT→CBAT→CHBAT→FUSEB; POOLB→CPOOLB→FCPOOLB.",
    "Train I/O: TOP→PIN→PRE→HALF→ADAMF→PRE2→PRE3.",
    "H-SERVE gate: |Δlp|≤ε vs EARLY and (wall↓ or tok/s↑) (formal PROMOTE; recipe=speed).",
    "H-ROUTE gate: not dominated by GALL or GRAPHF on (lp, wall) (formal PROMOTE).",
    "H-PARETO gate: audit live (≥1 pair); FLAG tok/s↑ & GFLOPs>tip·(1+δ) (formal PROMOTE; CBAT FLAG).",
    "H-ETRAIN gate: lp ≥ STAG−ε and e2e_wall < STAG (smoke PROMOTE / formal KILL — cache tax).",
    "H-FLOP: wall + tok/s + est. GFLOPs.",
    "H-MIX / H-FUSE / H-PARETO: PROTOCOL/audit only (not tips).",
]

NOTES = [
    "## Notes",
    "- Focus winners only. KILL code purged; history: `docs/results/nano-lm/archive/`.",
    "- Wave R complete (R4 PARETO PROMOTE; CBAT FLAG) — `.local/pesquisa.md`.",
    "- Smoke budgets are tentative; formal = 3 seeds + fit≠eval.",
    "- Agenda: `docs/NANO-STUDENT-AGENDA.md`.",
]
