# H-DIF smoke vs B2 (discrete diffusion nano)

Absorb-mask diffusion train; iterative remask decode at eval.
Kill if VRAM > 7 GiB, wall > 2× B2, or ≤ B2 quality.

| family | mean teacher_lp | mean wall_ms | peak VRAM MiB | Δ vs B2 | n |
|--------|-----------------|--------------|---------------|---------|---|
| B2 | -17.0918 | 86 | — | — | 3 |
| H-DIF | -17.8117 | 23 | 341 | -0.7199 | 3 |

**Decision: KILL (≤ B2)**

Commands: `npm run nano:dif` → `npm run nano:dif:report`.
