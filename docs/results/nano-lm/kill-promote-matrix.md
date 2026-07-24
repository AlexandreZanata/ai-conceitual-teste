# Nano student — kill / promote matrix (champions)

Source: `results/nano-lm/student-matrix/matrix.json`
Wall clock (matrix): 154.6s

Primary metric: teacher mean log-prob of student completions.
Full historical rows: `docs/results/nano-lm/archive/`.
H-SPEC gate: tokens/s > B3 and teacher_lp ≥ B3 − 0.05.
H-DEC / H-DECK / H-DECKL / H-POOL / H-EARLY: decode tips (see formal docs).
H-CUR / H-CURL / H-CURL2 / H-STAG: curriculum train (official = H-STAG lo=6, stages=4).
H-FLOP: report tokens/s + est. GFLOPs with wall (instrumentation).
H-LAY gate: lp ≥ EARLY−ε and (wall < EARLY or est_gflops < EARLY) (layer skip).
H-AMP gate: lp ≥ EARLY−ε and wall < EARLY (CUDA autocast bf16/fp16).
H-TIE gate: lp ≥ STAG−ε and (params < STAG or est_gflops < STAG) (UT-lite share).
H-PRUN gate: lp ≥ STAG−ε and est_gflops < STAG (magnitude prune; density FLOPs).
H-WIN gate: lp ≥ STAG−ε and est_gflops < STAG (local window attn).
H-SHORT gate: lp ≥ EARLY−ε and (wall < EARLY or est_gflops < EARLY) (short draft).
H-SOFT gate: lp ≥ STAG−ε and train ms/step < live STAG (soft-label cache).
H-BAT gate: |Δlp| ≤ ε vs serial EARLY and tok/s > serial (batched prompts).

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
- Official train tip: **H-STAG** (`formal-hstag-vs-hcurl2.md`).
- Official decode: **H-EARLY** (speed) / **H-POOL** (quality@wall).
- Waves A–H deepeners purged from code; see archive + `.local/pesquisa.md`.
- H-LAY smoke: `docs/results/nano-lm/hlay-vs-hearly.md` (PROMOTE wall↓; GFLOPs tie; formal deferred).
- H-LAY formal: `docs/results/nano-lm/formal-hlay-vs-hearly.md` (PROMOTE wall↓; GFLOPs tie; tip unchanged).
- H-AMP smoke: `docs/results/nano-lm/hamp-vs-hearly.md` (KILL — quality < EARLY−ε; wall↑).
- H-TIE smoke: `docs/results/nano-lm/htie-vs-hstag.md` (KILL — quality < STAG−ε; params↓).
- H-PRUN smoke: `docs/results/nano-lm/hprun-vs-hstag.md` (PROMOTE; density FLOPs; formal deferred).
- H-PRUN formal: `docs/results/nano-lm/formal-hprun-vs-hstag.md` (PROMOTE wall↓; quality↑; tip STAG unchanged).
- H-WIN smoke: `docs/results/nano-lm/hwin-vs-hstag.md` (KILL — quality < STAG−ε; FLOPs↓).
- H-SHORT smoke: `docs/results/nano-lm/hshort-vs-hearly.md` (PROMOTE wall↓; GFLOPs tie; formal deferred).
- H-SHORT formal: `docs/results/nano-lm/formal-hshort-vs-hearly.md` (PROMOTE wall↓ tiny; GFLOPs tie; tip unchanged).
- H-SOFT smoke: `docs/results/nano-lm/hsoft-vs-hstag.md` (KILL — no train ms/step win; H2D logits).
- H-BAT smoke: `docs/results/nano-lm/hbat-vs-hearly.md` (PROMOTE tok/s↑; formal deferred).
- H-BAT formal: `docs/results/nano-lm/formal-hbat-vs-hearly.md` (PROMOTE tok/s↑; tip EARLY unchanged).
- Smoke budgets are tentative; formal claims need 3 seeds + fit≠eval.
- Agenda: `docs/NANO-STUDENT-AGENDA.md`.
