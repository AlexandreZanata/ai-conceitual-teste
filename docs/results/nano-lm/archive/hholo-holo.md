# H-ABS-HOLO smoke — holographic checksum under 4-bit KV (**KILL**)

> Smoke **KILL**. Do not claim 4-bit+RFF dual-gate win from wall↓/story↑ with code↓. Tooling purged.

Wave X absurd sandbox: simulate 4-bit absmax K/V, restore via Rademacher RFF sketch (S=32, α=0.5) — not bare QCOMP ±1 shadow. Parent = bare H-EARLY on prog@128. Gate: not identity, both lps ≥ parent−ε, (code↑ or wall↓); audit recon_mse + sketch bytes.

Frozen: ε=0.05; bits=4; sketch_s=32; α=0.5; max_new=32; seeds=3; identity gate.

**Decision: KILL (code_lp -16.7888 < parent−ε -16.3192)**

## Arms

| arm | mean story_lp | mean code_lp | mean wall_ms | mean recon_mse | mean sketch_bytes | n |
|-----|---------------|--------------|--------------|----------------|-------------------|---|
| H-EARLY bare | -14.8854 | -16.2692 | 23 | 0.0000 | 0 | 12 |
| H-ABS-HOLO 4-bit S=32 | -14.2809 | -16.7888 | 15 | 0.0187 | 1974272 | 12 |

## Lesson

RFF checksum **did** change decode (story↑ Δ≈+0.60, wall↓, recon_mse≈0.019) but **broke** the code dual gate (Δ ≈ −0.52 vs parent−ε). Holographic restore under simulated 4-bit KV is not a free EARLY/QCOMP upgrade when code_teacher_lp falls. Next E.1: **H-ABS-PHASE** (complex/2D rotary θ) — not another QCOMP/RFF shadow blend.

Commands (purged): were `npm run nano:holo` / `nano:formal:hholo*`.
