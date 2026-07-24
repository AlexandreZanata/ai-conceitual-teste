"""Footer notes + gate blurbs for champion matrix markdown."""

GATES = [
    "H-SPEC gate: tokens/s > B3 and teacher_lp ≥ B3 − 0.05.",
    "H-DEC / H-DECK / H-DECKL / H-POOL / H-EARLY: decode tips (see formal docs).",
    "H-CUR / H-CURL / H-CURL2 / H-STAG: curriculum train (official = H-STAG lo=6, stages=4).",
    "H-FLOP: report tokens/s + est. GFLOPs with wall (instrumentation).",
    "H-LAY gate: lp ≥ EARLY−ε and (wall < EARLY or est_gflops < EARLY) (layer skip).",
    "H-AMP gate: lp ≥ EARLY−ε and wall < EARLY (CUDA autocast bf16/fp16).",
    "H-TIE gate: lp ≥ STAG−ε and (params < STAG or est_gflops < STAG) (UT-lite share).",
    "H-PRUN gate: lp ≥ STAG−ε and est_gflops < STAG (magnitude prune; density FLOPs).",
    "H-WIN gate: lp ≥ STAG−ε and est_gflops < STAG (local window attn).",
    "H-SHORT gate: lp ≥ EARLY−ε and (wall < EARLY or est_gflops < EARLY) (short draft).",
    "H-SOFT gate: lp ≥ STAG−ε and train ms/step < live STAG (soft-label cache).",
    "H-BAT gate: |Δlp| ≤ ε vs serial EARLY and tok/s > serial (batched prompts).",
]

NOTES = [
    "## Notes",
    "- Champion stack only. Purged H-ID history: `docs/results/nano-lm/archive/`.",
    "- Official train tip: **H-STAG** (`formal-hstag-vs-hcurl2.md`).",
    "- Official decode: **H-EARLY** (speed) / **H-POOL** (quality@wall).",
    "- Waves A–H deepeners purged from code; see archive + `.local/pesquisa.md`.",
    "- H-LAY smoke: `docs/results/nano-lm/hlay-vs-hearly.md` (PROMOTE wall↓; GFLOPs tie; formal deferred).",
    "- H-LAY formal: `docs/results/nano-lm/formal-hlay-vs-hearly.md` (PROMOTE wall↓; GFLOPs tie; tip unchanged).",
    "- H-AMP smoke: `docs/results/nano-lm/hamp-vs-hearly.md` (KILL — quality < EARLY−ε; wall↑).",
    "- H-TIE smoke: `docs/results/nano-lm/htie-vs-hstag.md` (KILL — quality < STAG−ε; params↓).",
    "- H-PRUN smoke: `docs/results/nano-lm/hprun-vs-hstag.md` (PROMOTE; density FLOPs; formal deferred).",
    "- H-WIN smoke: `docs/results/nano-lm/hwin-vs-hstag.md` (KILL — quality < STAG−ε; FLOPs↓).",
    "- H-SHORT smoke: `docs/results/nano-lm/hshort-vs-hearly.md` (PROMOTE wall↓; GFLOPs tie; formal deferred).",
    "- H-SOFT smoke: `docs/results/nano-lm/hsoft-vs-hstag.md` (KILL — no train ms/step win; H2D logits).",
    "- H-BAT smoke: `docs/results/nano-lm/hbat-vs-hearly.md` (PROMOTE tok/s↑; formal deferred).",
    "- H-BAT formal: `docs/results/nano-lm/formal-hbat-vs-hearly.md` (PROMOTE tok/s↑; tip EARLY unchanged).",
    "- Smoke budgets are tentative; formal claims need 3 seeds + fit≠eval.",
    "- Agenda: `docs/NANO-STUDENT-AGENDA.md`.",
]
