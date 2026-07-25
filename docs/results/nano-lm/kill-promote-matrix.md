# Nano student — kill / promote matrix (champions)

Source: `results/nano-lm/student-matrix/matrix.json`
Wall clock (matrix): 154.6s

Primary metric: teacher mean log-prob of student completions.
Full historical rows: `docs/results/nano-lm/archive/`.
Tips: H-STAG′ / H-EARLY / H-POOL (TIPD promoted train tip).
Primary recipe: H-PACK (serve-fast; elongated+ood+howto+prog+btc; not ood_long).
Train: H-TPACK + H-AMORT; quality serve H-QPACK in-harness only.

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
- Deploy: `docs/results/nano-lm/RECIPES.md` + DEPL/DOM/PROG/BTC formals.
- Wave V COMPLETE; Wave W ACTIVE — curated KB (`.local/pesquisa.md`).
- H-PROG smoke+formal PROMOTE (`formal-hprog-programming.md`).
- H-BTC smoke+formal PROMOTE (`formal-hbtc-bitcoin.md`).
- H-MIXD smoke PROMOTE (`hmixd-mix.md`); formal pending.
- EvoGen survival archived: `docs/archive/evogen/`.
- Agenda: `docs/NANO-STUDENT-AGENDA.md`.
