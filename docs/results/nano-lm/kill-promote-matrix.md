# Nano student — kill / promote matrix

Source: `results/nano-lm/student-matrix/matrix.json`
Wall clock (matrix): 154.6s

Primary metric: teacher (TinyStories-33M) mean log-prob of student completions (higher / less negative is better).
H-SPEC gate: tokens/s > B3 and teacher_lp ≥ B3 − 0.05.
H-LAM gate: stable and teacher_lp > H-BAL.
H-ELI gate: no diversity collapse and teacher_lp > H-SEL.
H-ENT gate: heads not collapsed and teacher_lp > B2.
H-ANN gate: teacher_lp > KD-cos (cosine schedule control).
H-FIT gate: teacher_lp > H-SEL (claim-aligned fitness).
H-TOU gate: teacher_lp > H-SEL (tournament vs truncation).
H-XOV gate: no diversity collapse and teacher_lp > H-SEL.

| family | mean teacher_lp | Δ vs B2 | mean wall_ms | tok/s | n | decision |
|--------|-----------------|---------|--------------|-------|---|-----------|
| B0 | -16.9633 | +0.1285 | 74 | — | 3 | control |
| B1 | -17.3335 | -0.2417 | 41 | — | 3 | control |
| B2 | -17.0918 | — | 86 | — | 3 | BASELINE (claim gate) |
| B3 | -17.0918 | +0.0000 | 72 | 679.9 | 3 | decode control (AR) |
| B4 | -17.0202 | +0.0716 | 55 | 585.9 | 3 | decode control (BoN) |
| H-SPEC | -1.3358 | +15.7560 | 239 | 134.1 | 3 | KILL (no speedup vs B3) |
| H-DEC | -16.9235 | +0.1683 | — | — | 3 | PROMOTE (beats fixed BoN/B4) |
| H-SEL | -17.0080 | +0.0838 | 51 | — | 3 | PROMOTE (beats B2) |
| H-BAL | -17.3913 | -0.2996 | 54 | — | 3 | KILL / hold (≤ B2) |
| H-LAM | -17.0049 | +0.0869 | 54 | — | 3 | PROMOTE (beats H-BAL) |
| H-ELI | -17.4219 | -0.3301 | 52 | — | 3 | KILL / hold (≤ H-SEL) |
| H-FIT | -16.8318 | +0.2600 | 38 | — | 3 | PROMOTE (beats H-SEL) |
| H-TOU | -17.4219 | -0.3301 | 56 | — | 3 | KILL / hold (≤ H-SEL) |
| H-XOV | -16.2818 | +0.8100 | 53 | — | 3 | PROMOTE (beats H-SEL, diversity ok) |
| H-ENT | -16.9916 | +0.1002 | 57 | — | 3 | KILL (collapsed to one head) |
| KD-cos | -17.3873 | -0.2955 | 63 | — | 3 | schedule control (cosine KD) |
| H-ANN | -17.3793 | -0.2876 | 41 | — | 3 | PROMOTE (beats cosine KD) |
| H-BON | -17.2071 | -0.1153 | 143 | — | 3 | KILL / hold (≤ B2) |
| H-MAE | -17.2136 | -0.1218 | 212 | — | 3 | KILL / hold (≤ B2) |
| H-SUP | -0.5197 | +16.5721 | — | — | 1 | KILL (≤ uniform BoN) |
| H-INT | -0.5197 | +16.5721 | — | — | 1 | KILL (≤ uniform BoN) |
| BoN-uniform | -0.3698 | +16.7220 | — | — | 1 | ablation control |

## Notes

- Smoke budgets (few steps / small pop). Formal claims need longer runs.
- B3/B4/H-SPEC decode on B2 checkpoints; H-SPEC vs B3 on speed+quality.
- H-SPEC smoke detail: `docs/results/nano-lm/hspec-vs-b3.md`.
- H-BAL smoke detail: `docs/results/nano-lm/hbal-vs-b2.md`.
- H-DEC smoke detail: `docs/results/nano-lm/hdec-vs-b4.md`.
- H-LAM smoke detail: `docs/results/nano-lm/hlam-vs-hbal.md`.
- H-ELI smoke detail: `docs/results/nano-lm/heli-vs-hsel.md`.
- H-ENT smoke detail: `docs/results/nano-lm/hent-vs-b2.md`.
- H-ANN smoke detail: `docs/results/nano-lm/hann-vs-kdcos.md`.
- H-FIT smoke detail: `docs/results/nano-lm/hfit-vs-hsel.md`.
- H-TOU smoke detail: `docs/results/nano-lm/htou-vs-hsel.md`.
- H-XOV smoke detail: `docs/results/nano-lm/hxov-vs-hsel.md`.
- H-SUP/H-INT rows are decode selection scores on teacher, not trained students.
- H-SEL smoke PROMOTE was reversed on formal — see `formal-hsel-vs-b2.md`.
- Agenda: `docs/NANO-STUDENT-AGENDA.md`.
