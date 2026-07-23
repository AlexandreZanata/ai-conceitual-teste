# Nano student — kill / promote matrix

Source: `results/nano-lm/student-matrix/matrix.json`
Wall clock (matrix): 154.6s

Primary metric: teacher (TinyStories-33M) mean log-prob of student completions (higher / less negative is better).

| family | mean teacher_lp | Δ vs B2 | mean wall_ms | n | decision |
|--------|-----------------|---------|--------------|---|-----------|
| B0 | -16.9633 | +0.1285 | 74 | 3 | control |
| B1 | -17.3335 | -0.2417 | 41 | 3 | control |
| B2 | -17.0918 | — | 86 | 3 | BASELINE (claim gate) |
| H-SEL | -17.0080 | +0.0838 | 51 | 3 | PROMOTE (beats B2) |
| H-BON | -17.2071 | -0.1153 | 143 | 3 | KILL / hold (≤ B2) |
| H-MAE | -17.2136 | -0.1218 | 212 | 3 | KILL / hold (≤ B2) |
| H-SUP | -0.5197 | +16.5721 | — | 1 | KILL (≤ uniform BoN) |
| H-INT | -0.5197 | +16.5721 | — | 1 | KILL (≤ uniform BoN) |
| BoN-uniform | -0.3698 | +16.7220 | — | 1 | ablation control |

## Notes

- Smoke budgets (few steps / small pop). Formal claims need longer runs.
- H-SUP/H-INT rows are decode selection scores on teacher, not trained students.
- Agenda: `docs/NANO-STUDENT-AGENDA.md`.
- **Formal follow-up:** H-SEL smoke PROMOTE was **reversed** — see [formal-hsel-vs-b2.md](formal-hsel-vs-b2.md) (B2 beats H-SEL by ~1.59 teacher log-prob on 8 prompts × 3 seeds). H-SEL → **KILL / hold** for now.
