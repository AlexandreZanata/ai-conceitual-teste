# Nano student — kill / promote matrix (champions)

Source: `results/nano-lm/student-matrix/matrix.json`
Wall clock (matrix): 154.6s

Primary metric: teacher mean log-prob of student completions.
Full historical rows: `docs/results/nano-lm/archive/`.
H-SPEC gate: tokens/s > B3 and teacher_lp ≥ B3 − 0.05.
H-DEC / H-DECK / H-DECKL / H-POOL / H-EARLY: decode tips (see formal docs).
H-CUR / H-CURL / H-CURL2: curriculum train tips (official train = H-CURL2 seq_lo=6).
H-EAR2 gate: lp ≥ EARLY−ε and wall < EARLY (widened early gene).
H-BUD gate: not dominated by EARLY on (lp, wall); quality ≥ EARLY−ε.
H-THIN gate: lp ≥ CURL−ε and wall < CURL on same EARLY decode.
H-Q8 gate: lp ≥ CURL−ε and wall < CURL (INT8 dynamic on same EARLY).
H-EARS gate: lp ≥ EARLY−ε and wall < EARLY (scheduled thr).
H-CURL2 gate: best seq_lo on {4,6,8,10,12} > tip lo=8.
H-COMP gate: lp ≥ EARLY−ε and wall < EARLY (torch.compile).
H-PROX gate: claim lp ≥ POOL−ε (CE-only fit; teacher claim).
H-POOL2 gate: lp ≥ POOL−ε and fit teacher_fwd < POOL (tighter search).
H-CURD gate: teacher_lp > H-CURL2 tip @ equal steps (NLL bins; xor length).
H-STEP gate: claim lp ≥ H-CURL2 tip (early-stop on fit teacher_lp plateau).
H-ALAT gate: teacher_lp > H-CURL2 tip (α/T schedule under CURL stages).
H-FLOP gate: finite mean_tokens_per_s + mean_est_gflops on scored families.
H-EARF gate: lp ≥ EARLY−ε and est_gflops < EARLY (FLOP-aware search).
H-EXIT gate: lp ≥ EARLY−ε and est_gflops < EARLY (min_new↓ + n=1).
H-MID gate: lp ≥ EARLY−ε and est_gflops < EARLY (min_new∈{4,8} + warm-start).

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
- Champion stack only. Purged H-ID history: `docs/results/nano-lm/archive/`.
- H-EAR2 smoke: `docs/results/nano-lm/hear2-vs-hearly.md` (KILL — quality < EARLY−ε).
- H-BUD smoke: `docs/results/nano-lm/hbud-vs-hearly.md` (KILL — quality < EARLY−ε).
- H-THIN: smoke PROMOTE (`hthin-vs-hcurl.md`); formal **KILL** (`formal-hthin-vs-hcurl.md` — Δ−0.33 vs CURL; wall↓).
- H-Q8 smoke: `docs/results/nano-lm/hq8-vs-hcurl.md` (KILL — no wall win vs CUDA tip; CPU dynamic INT8).
- H-EARS smoke: `docs/results/nano-lm/hears-vs-hearly.md` (KILL — quality < EARLY−ε).
- H-CURL2: smoke PROMOTE (`hcurl2-vs-hcurl.md` lo=12); formal **PROMOTE** (`formal-hcurl2-vs-hcurl.md` lo=6).
- H-COMP smoke: `docs/results/nano-lm/hcomp-vs-hearly.md` (KILL — no wall win; CUDAGraph re-record).
- H-PROX smoke: `docs/results/nano-lm/hprox-vs-hpool.md` (KILL — claim quality < POOL−ε).
- H-POOL2 smoke: `docs/results/nano-lm/hpool2-vs-hpool.md` (KILL — quality < POOL−ε; fit-fwd↓).
- H-CURD: smoke PROMOTE (`hcurd-vs-hcurl2.md` Δ+0.01); formal **KILL** (`formal-hcurd-vs-hcurl2.md` Δ−1.16).
- H-STEP smoke: `docs/results/nano-lm/hstep-vs-hcurl2.md` (KILL — Δ−0.23 vs tip; steps↓).
- H-ALAT (αT) smoke: `docs/results/nano-lm/halat-vs-hcurl2.md` (KILL — Δ−0.23 vs tip).
- H-FLOP smoke: `docs/results/nano-lm/hflop-instrumentation.md` (PROMOTE — tps+GFLOPs live; EARLY wall↓ but GFLOPs↑).
- H-EARF smoke: `docs/results/nano-lm/hearf-vs-hearly.md` (KILL — no FLOP win; same est GFLOPs as tip).
- H-EXIT smoke: `docs/results/nano-lm/hexit-vs-hearly.md` (KILL — quality Δ−0.44; GFLOPs↓).
- H-MID: smoke PROMOTE (`hmid-vs-hearly.md`); formal **KILL** (`formal-hmid-vs-hearly.md` — quality Δ−0.51).
- Smoke budgets are tentative; formal claims need 3 seeds + fit≠eval.
- Agenda: `docs/NANO-STUDENT-AGENDA.md`.
