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
H-NIC gate: diversity↑ and teacher_lp > H-SEL.
H-MUT gate: teacher_lp > H-SEL (adaptive vs fixed mutate).
H-RAN gate: teacher_lp > H-SEL (rank vs truncation).
H-AGE gate: teacher_lp > H-SEL (ALPS vs flat).
H-MOR gate: teacher_lp > H-SEL (mortality vs no cull).
H-SPE gate: teacher_lp > H-SEL (islands vs single).
H-SEX gate: teacher_lp > H-SEL (mate choice vs truncation).
H-ANTI gate: teacher_lp > H-SEL (anti-selection vs truncation).
H-TAX gate: teacher_lp > H-SEL (wealth tax vs no tax).
H-CAN gate: no NaN and teacher_lp > H-SEL (LN cannibalism).
H-PAR gate: parasite does not dominate and teacher_lp > H-SEL.
H-SYM gate: teacher_lp > H-SEL (obligate pair vs truncation).
H-FOS gate: teacher_lp > H-SEL (fossil resurrect vs no-resurrect).
H-ZOM gate: no diverge and teacher_lp > H-SEL (zombie reinject).
H-LOTU gate: teacher_lp > H-SEL (underdog lottery vs truncation).
H-GLD gate: teacher_lp > H-FIT (Goldilocks vs max-lp fitness).
H-SEA gate: teacher_lp > H-FIT (seasonal vs fixed H-FIT).
H-RPS gate: ≥2 niches and teacher_lp > H-SEL (RPS niches).
H-CAT gate: teacher_lp > H-SEL (catastrophe vs steady).
H-HIB gate: teacher_lp > H-SEL (hibernate vs full eval).
H-SHO gate: teacher_lp > H-SEL (shock vs plain mutate).
H-HOLD gate: no overfit and teacher_lp > B2 (holdout fit≠eval).
H-FXS gate: teacher_lp > max(H-FIT, H-XOV) (FIT×XOV×SHO stack).
H-LOFI gate: teacher_lp ≥ H-FIT−ε and wall_save (fewer teacher forwards).
H-ENT2 gate: heads not collapsed and teacher_lp > B2 (TV floor).
H-ENT3 gate: no collapse/chaos and teacher_lp > B2 (max TV + mix KD).
H-TMN gate: lp ≥ max(H-TYP,H-MINP)−ε and wall < min tips (TYP×MINP stack).
H-TPE gate: teacher_lp ≥ H-TYP−ε and wall < tip (evolved typ_mass).
H-CUR gate: teacher_lp > B2 (length-curriculum KD).
H-CUR2 gate: best n_stages∈{2,3,4,5} > H-CUR (n=3).
H-CURL gate: best seq_lo∈{8,16,32} > H-CUR (lo=16).
H-CURT gate: teacher_lp > H-CUR (adopted n=5, lo=8).
H-SYS gate: arm lp > CURL default and > tip@B2 (free lunch).

| family | mean teacher_lp | Δ vs B2 | mean wall_ms | tok/s | n | decision |
|--------|-----------------|---------|--------------|-------|---|-----------|
| B0 | -16.9633 | +0.1285 | 74 | — | 3 | control |
| B1 | -17.3335 | -0.2417 | 41 | — | 3 | control |
| B2 | -17.0918 | — | 86 | — | 3 | BASELINE (claim gate) |
| B3 | -17.0918 | +0.0000 | 72 | 679.9 | 3 | decode control (AR) |
| B4 | -17.0202 | +0.0716 | 55 | 585.9 | 3 | decode control (BoN) |
| H-SPEC | -1.3358 | +15.7560 | 239 | 134.1 | 3 | KILL (no speedup vs B3) |
| H-DEC | -16.9235 | +0.1683 | — | — | 3 | PROMOTE smoke; formal PROMOTE vs B4 |
| H-SEL | -17.0080 | +0.0838 | 51 | — | 3 | PROMOTE (beats B2) |
| H-BAL | -17.3913 | -0.2996 | 54 | — | 3 | KILL / hold (≤ B2) |
| H-LAM | -17.0049 | +0.0869 | 54 | — | 3 | PROMOTE smoke; formal KILL vs H-BAL |
| H-ELI | -17.4219 | -0.3301 | 52 | — | 3 | KILL / hold (≤ H-SEL) |
| H-FIT | -16.8318 | +0.2600 | 38 | — | 3 | PROMOTE smoke; formal KILL vs B2 |
| H-TOU | -17.4219 | -0.3301 | 56 | — | 3 | KILL / hold (≤ H-SEL) |
| H-XOV | -16.2818 | +0.8100 | 53 | — | 3 | PROMOTE smoke; formal KILL vs B2 |
| H-NIC | -17.0080 | +0.0838 | 62 | — | 3 | KILL / hold (≤ H-SEL) |
| H-MUT | -17.4219 | -0.3301 | 53 | — | 3 | KILL / hold (≤ H-SEL) |
| H-RAN | -17.6331 | -0.5414 | 54 | — | 3 | KILL / hold (≤ H-SEL) |
| H-AGE | -17.4219 | -0.3301 | 56 | — | 3 | KILL / hold (≤ H-SEL) |
| H-MOR | -17.2746 | -0.1828 | 57 | — | 3 | KILL / hold (≤ H-SEL) |
| H-SPE | -17.2271 | -0.1353 | 54 | — | 3 | KILL / hold (≤ H-SEL) |
| H-SEX | -17.0612 | +0.0306 | 66 | — | 3 | KILL / hold (≤ H-SEL) |
| H-ANTI | -17.6378 | -0.5461 | 69 | — | 3 | KILL / hold (≤ H-SEL) |
| H-TAX | -17.0837 | +0.0080 | 55 | — | 3 | KILL / hold (≤ H-SEL) |
| H-CAN | -17.0080 | +0.0838 | 60 | — | 3 | KILL / hold (≤ H-SEL) |
| H-PAR | -17.6378 | -0.5461 | 54 | — | 3 | KILL (parasite dominates) |
| H-SYM | -16.8181 | +0.2737 | 72 | — | 3 | PROMOTE smoke; formal KILL vs B2 |
| H-FOS | -17.0080 | +0.0838 | 61 | — | 3 | KILL / hold (≤ H-SEL) |
| H-ZOM | -17.4219 | -0.3301 | 52 | — | 3 | KILL / hold (≤ H-SEL) |
| H-LOTU | -17.2746 | -0.1828 | 54 | — | 3 | KILL / hold (≤ H-SEL) |
| H-GLD | -16.8318 | +0.2600 | 39 | — | 3 | KILL / hold (≤ max-lp fitness) |
| H-SEA | -17.3290 | -0.2373 | 40 | — | 3 | KILL / hold (≤ max-lp fitness) |
| H-RPS | -17.5223 | -0.4305 | 58 | — | 3 | KILL (collapsed to 1 niche) |
| H-CAT | -17.5397 | -0.4479 | 57 | — | 3 | KILL / hold (≤ H-SEL) |
| H-HIB | -17.4219 | -0.3301 | 54 | — | 3 | KILL / hold (≤ H-SEL) |
| H-SHO | -16.9601 | +0.1317 | 52 | — | 3 | PROMOTE smoke; formal KILL vs B2 |
| H-HOLD | -16.7060 | +0.3858 | 45 | — | 3 | PROMOTE (beats B2, holdout ok) |
| H-FXS | -17.1325 | -0.0407 | 44 | — | 3 | KILL / hold (≤ max FIT/XOV) |
| H-LOFI | -17.2565 | -0.1647 | 47 | — | 3 | KILL (worse quality than H-FIT) |
| H-ENT2 | -16.9916 | +0.1002 | 149 | — | 3 | KILL (collapsed again) |
| H-ENT3 | -16.9916 | +0.1002 | 115 | — | 3 | KILL (collapsed) |
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
- H-NIC smoke detail: `docs/results/nano-lm/hnic-vs-hsel.md`.
- H-MUT smoke detail: `docs/results/nano-lm/hmut-vs-hsel.md`.
- H-RAN smoke detail: `docs/results/nano-lm/hran-vs-hsel.md`.
- H-AGE smoke detail: `docs/results/nano-lm/hage-vs-hsel.md`.
- H-MOR smoke detail: `docs/results/nano-lm/hmor-vs-hsel.md`.
- H-SPE smoke detail: `docs/results/nano-lm/hspe-vs-hsel.md`.
- H-SEX smoke detail: `docs/results/nano-lm/hsex-vs-hsel.md`.
- H-ANTI smoke detail: `docs/results/nano-lm/hanti-vs-hsel.md`.
- H-TAX smoke detail: `docs/results/nano-lm/htax-vs-hsel.md`.
- H-CAN smoke detail: `docs/results/nano-lm/hcan-vs-hsel.md`.
- H-PAR smoke detail: `docs/results/nano-lm/hpar-vs-hsel.md`.
- H-SYM smoke detail: `docs/results/nano-lm/hsym-vs-hsel.md`.
- H-FOS smoke detail: `docs/results/nano-lm/hfos-vs-hsel.md`.
- H-ZOM smoke detail: `docs/results/nano-lm/hzom-vs-hsel.md`.
- H-LOTU smoke detail: `docs/results/nano-lm/hlotu-vs-hsel.md`.
- H-GLD smoke detail: `docs/results/nano-lm/hgld-vs-hfit.md`.
- H-SEA smoke detail: `docs/results/nano-lm/hsea-vs-hfit.md`.
- H-RPS smoke detail: `docs/results/nano-lm/hrps-vs-hsel.md`.
- H-CAT smoke detail: `docs/results/nano-lm/hcat-vs-hsel.md`.
- H-HIB smoke detail: `docs/results/nano-lm/hhib-vs-hsel.md`.
- H-SHO smoke detail: `docs/results/nano-lm/hsho-vs-hsel.md`.
- H-HOLD smoke detail: `docs/results/nano-lm/hhold-vs-b2.md`.
- H-FXS smoke detail: `docs/results/nano-lm/hfxs-vs-fit-xov.md`.
- H-LOFI smoke detail: `docs/results/nano-lm/hlofi-vs-hfit.md`.
- H-ENT2 smoke detail: `docs/results/nano-lm/hent2-vs-b2.md`.
- H-ENT3 smoke detail: `docs/results/nano-lm/hent3-vs-b2.md`.
- H-TMN smoke detail: `docs/results/nano-lm/htmn-vs-tips.md` (KILL — wall ≥ tips).
- H-TPE smoke detail: `docs/results/nano-lm/htpe-vs-htyp.md` (KILL — quality < tip).
- H-CUR smoke/formal: `docs/results/nano-lm/hcur-vs-b2.md`, `formal-hcur-vs-b2.md` (PROMOTE).
- H-CUR2 smoke/formal: `docs/results/nano-lm/hcur2-vs-hcur.md`, `formal-hcur2-vs-hcur.md` (PROMOTE; best n=5).
- H-CURL smoke/formal: `docs/results/nano-lm/hcurl-vs-hcur.md`, `formal-hcurl-vs-hcur.md` (PROMOTE; best lo=8).
- H-CURT smoke: `docs/results/nano-lm/hcurt-vs-hcur.md` (KILL — joint knobs ≤ tip).
- H-SYS smoke: `docs/results/nano-lm/hsys-vs-tips.md` (KILL — paste free lunch).
- H-SUP/H-INT rows are decode selection scores on teacher, not trained students.
- H-SEL smoke PROMOTE was reversed on formal — see `formal-hsel-vs-b2.md`.
- H-HOLD smoke PROMOTE was reversed on formal — see `formal-hhold-vs-b2.md`.
- H-XOV smoke PROMOTE was reversed on formal — see `formal-hxov-vs-b2.md`.
- H-FIT smoke PROMOTE was reversed on formal — see `formal-hfit-vs-b2.md`.
- H-SYM smoke PROMOTE was reversed on formal — see `formal-hsym-vs-b2.md`.
- H-DEC smoke PROMOTE confirmed on formal — see `formal-hdec-vs-b4.md`.
- H-SHO smoke PROMOTE was reversed on formal — see `formal-hsho-vs-b2.md`.
- H-LAM smoke PROMOTE was reversed on formal — see `formal-hlam-vs-hbal.md`.
- Agenda: `docs/NANO-STUDENT-AGENDA.md`.