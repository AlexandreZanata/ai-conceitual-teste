# Nano student — kill / promote matrix (champions)

Source: `results/nano-lm/student-matrix/matrix.json`
Wall clock (matrix): 154.6s

Primary metric: teacher mean log-prob of student completions.
Full historical rows: `docs/results/nano-lm/archive/`.
H-SPEC gate: tokens/s > B3 and teacher_lp ≥ B3 − 0.05.
Tips: H-STAG train / H-EARLY speed / H-POOL quality@wall.
Serving utils: FLASH/CHUNK/CHB + LAYB/FLAYB + GRAPH/GRAPHF/GALL + SERVE + ROUTE.
Batch utils: BAT→CBAT→CHBAT→FUSEB; POOLB→CPOOLB→FCPOOLB.
Train I/O: TOP→PIN→PRE→HALF→ADAMF→PRE2→PRE3.
H-SERVE gate: |Δlp|≤ε vs EARLY and (wall↓ or tok/s↑) (formal PROMOTE; recipe=speed).
H-ROUTE gate: not dominated by GALL or GRAPHF on (lp, wall) (formal PROMOTE).
H-PARETO gate: audit live (≥1 pair); FLAG tok/s↑ & GFLOPs>tip·(1+δ) (formal PROMOTE; CBAT FLAG).
H-SROUTE gate: not dominated by SERVE on (lp, wall) (formal PROMOTE; SERVE keeps min-wall).
H-SKIP gate: wall↓ or tok/s↑ vs BAT and GFLOPs ≤ BAT·(1+δ) (formal PROMOTE; CBAT demoted).
H-PACK gate: SERVE |Δlp|≤ε + win; SROUTE lp≥EARLY−ε + win (formal PROMOTE; packs frozen).
H-BPACK gate: SKIP+LAYB |Δlp|≤ε + win; SKIP GFLOPs≤EARLY·(1+δ) (formal PROMOTE).
H-QPACK gate: FLAYB lp≥POOL−ε + wall/tok/s win (formal PROMOTE; quality pack).
H-TPACK gate: PRE3 lp≥STAG−ε + ms/step < STAG (formal PROMOTE; not e2e).
H-ETRAIN gate: lp ≥ STAG−ε and e2e_wall < STAG (smoke PROMOTE / formal KILL — cache tax).
H-FLOP: wall + tok/s + est. GFLOPs.
H-MIX / H-FUSE / H-PARETO / H-PACK / H-BPACK / H-QPACK / H-TPACK: PROTOCOL/audit only (not tips).

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
- Focus winners only. KILL code purged; history: `docs/results/nano-lm/archive/`.
- Wave T complete (BPACK/QPACK/TPACK formal PROMOTE) — parked; `.local/pesquisa.md`.
- Smoke budgets are tentative; formal = 3 seeds + fit≠eval.
- Agenda: `docs/NANO-STUDENT-AGENDA.md`.
