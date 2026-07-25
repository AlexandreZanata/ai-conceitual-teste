# H-PRUNF smoke — PRUN ckpt under FLAYB decode

Same dual-budget FLAYB path on frozen `HPRUN` (mag-prune + recover) vs control H-FLAYB on B2. GFLOPs density-scaled. Kill if |Δlp| > ε vs H-FLAYB or no wall/GFLOPs win.
Prompt pack: smoke+fit elongated (`n_prompts=4`); budgets=`[16, 64]` target_tokens=`128`; mode `PRUN under FLAYB vs B2+FLAYB; dual-budget; long prompts`.
PRUN densities per seed: `[0.7000001810090166, 0.7000001810090166, 0.7000001810090166]`.

| family | mean teacher_lp | Δ lp | mean tok/s | Δ tok/s | mean wall_ms/prompt | Δ wall | mean est GFLOPs | Δ GFLOPs | n |
|--------|-----------------|------|------------|---------|---------------------|--------|-----------------|----------|---|
| H-FLAYB | -10.4872 | — | 2273.6 | — | 22 | — | 43.431 | — | 3 |
| H-PRUNF | -8.1923 | +2.2949 | 2697.8 | +424.2 | 14 | -9 | 30.402 | -13.029 | 3 |

**Decision: KILL (lp change vs H-FLAYB)**

Thin+prune util under FLAYB — tip POOL / util FLAYB / PRUN unchanged.

Commands: `npm run nano:prunf` → `npm run nano:prunf:report`.
