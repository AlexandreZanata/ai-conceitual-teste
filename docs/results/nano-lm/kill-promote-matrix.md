# Nano student — kill / promote matrix

Source: `results/nano-lm/student-matrix/matrix.json`
Wall clock (matrix): 154.6s

Primary metric: teacher (TinyStories-33M) mean log-prob of student completions (higher / less negative is better).
H-SPEC gate: tokens/s > B3 and teacher_lp ≥ B3 − 0.05.

| family | mean teacher_lp | Δ vs B2 | mean wall_ms | tok/s | n | decision |
|--------|-----------------|---------|--------------|-------|---|-----------|
| B0 | -16.9633 | +0.1285 | 74 | — | 3 | control |
| B1 | -17.3335 | -0.2417 | 41 | — | 3 | control |
| B2 | -17.0918 | — | 86 | — | 3 | BASELINE (claim gate) |
| B3 | -17.0918 | +0.0000 | 72 | 679.9 | 3 | decode control (AR) |
| B4 | -17.0202 | +0.0716 | 55 | 585.9 | 3 | decode control (BoN) |
| H-SPEC | -1.3358 | +15.7560 | 239 | 134.1 | 3 | KILL (no speedup vs B3) |
| H-SEL | -17.0080 | +0.0838 | 51 | — | 3 | PROMOTE (beats B2) |
| H-BON | -17.2071 | -0.1153 | 143 | — | 3 | KILL / hold (≤ B2) |
| H-MAE | -17.2136 | -0.1218 | 212 | — | 3 | KILL / hold (≤ B2) |
| H-SUP | -0.5197 | +16.5721 | — | — | 1 | KILL (≤ uniform BoN) |
| H-INT | -0.5197 | +16.5721 | — | — | 1 | KILL (≤ uniform BoN) |
| BoN-uniform | -0.3698 | +16.7220 | — | — | 1 | ablation control |

## Notes

- Smoke budgets (few steps / small pop). Formal claims need longer runs.
- B3/B4/H-SPEC decode on B2 checkpoints; H-SPEC vs B3 on speed+quality.
- H-SPEC smoke detail: `docs/results/nano-lm/hspec-vs-b3.md`.
- H-SUP/H-INT rows are decode selection scores on teacher, not trained students.
- H-SEL smoke PROMOTE was reversed on formal — see `formal-hsel-vs-b2.md`.
- Agenda: `docs/NANO-STUDENT-AGENDA.md`.
