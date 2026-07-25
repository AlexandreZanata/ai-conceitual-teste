# Nano student — kill / promote matrix (champions)

Source: `results/nano-lm/student-matrix/matrix.json`
Wall clock (matrix): 154.6s

Primary metric: teacher mean log-prob of student completions.
Full historical rows: `docs/results/nano-lm/archive/`.
H-SPEC gate: tokens/s > B3 and teacher_lp ≥ B3 − 0.05.
H-DEC / H-DECK / H-DECKL / H-POOL / H-EARLY: decode tips (see formal docs).
H-CUR / H-CURL / H-CURL2 / H-STAG: curriculum train (official = H-STAG lo=6, stages=4).
H-FLOP: report tokens/s + est. GFLOPs with wall (instrumentation).
Decode utils: LAY/SHORT/FLASH/KVSEL/CHUNK/CHB/BAT/CBAT/POOLB (tips unchanged).
Train utils: PRUN/TOP/DEPTH/PIN (tip STAG/TOP unchanged).
H-Q4 gate: lp ≥ DEPTH−ε and wall < DEPTH (formal KILL — quality cliff).
H-MIX / H-FUSE / H-CFUSE: PROTOCOL only (not tip H-IDs); CFUSE smoke KILL.

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
- Focus stack: systems + batch + TOP/PIN + DEPTH. Archive: `docs/results/nano-lm/archive/`.
- Official tips: **H-STAG** / **H-EARLY** / **H-POOL**.
- H-TOPK / H-Q4 formal KILL; H-CFUSE smoke KILL; **H-CBAT** / **H-CHB** formal PROMOTE. Wave L next **H-ASYNC** (`.local/pesquisa.md`).
- Smoke budgets are tentative; formal claims need 3 seeds + fit≠eval.
- Agenda: `docs/NANO-STUDENT-AGENDA.md`.
