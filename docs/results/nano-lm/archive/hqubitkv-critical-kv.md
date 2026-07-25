# H-Q-QUBITKV smoke — critical KV + residual sketch (**KILL**)

> Smoke **KILL**. Do not claim QubitCache-style critical+sketch long-L serve. Tooling purged.

Wave X compression: prefill KV@256, keep top 15% positions by ‖K‖₂ classical, Rademacher-sketch residual → S=32 slots, decode on `cat(crit, sketch)`. Parent = EARLY@128. Inspiration: QubitCache (critical KV classical + amplitude/sketch residual; no quantum hardware). Not bare shadow (H-QCOMP).

Frozen: ε=0.05; crit_frac=0.15; residual_slots=32; wall_slack=50ms; seeds=3; max_new=32; prog pack.

**Decision: KILL (code_lp@L256 −18.1442 < C0−ε −16.3192)**

## Arms

| arm | mean story_lp | mean code_teacher_lp | mean wall_ms | kv_bytes | full_kv_bytes | n_crit | recon_mse | n |
|-----|---------------|----------------------|--------------|----------|---------------|--------|-----------|---|
| C0 EARLY@128 | -14.8854 | -16.2692 | 22 | — | — | — | — | 12 |
| H-Q-QUBITKV@256 | -15.2400 | -18.1442 | 14 | 76032 | 289792 | 42.3 | 0.2803 | 12 |

## Lesson

Critical-token keep + residual sketch **won mem** (76032 < 289792) and **wall↓**, but **lowered** `code_teacher_lp` (Δ ≈ −1.83 vs C0−ε) and story slightly. Selecting by ‖K‖₂ alone does not preserve code quality at L=256 — need a different long-L mechanism (hierarchical / GENC search over compress knobs), not another KV reorder+sketch.

Commands (purged): were `npm run nano:qubitkv` / `nano:formal:hqubitkv*`.
