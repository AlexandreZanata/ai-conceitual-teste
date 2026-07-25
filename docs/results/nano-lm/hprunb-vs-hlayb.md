# H-PRUNB smoke — PRUN ckpt under LAYB decode

Same dual-budget LAYB path on frozen `HPRUN` (mag-prune + recover) vs control H-LAYB on B2. GFLOPs density-scaled. Kill if |Δlp| > ε vs H-LAYB or no wall/GFLOPs win.
Prompt pack: smoke+fit elongated (`n_prompts=4`); budgets=`[16, 64]` target_tokens=`128`; mode `PRUN under LAYB vs B2+LAYB; dual-budget; long prompts`.
PRUN densities per seed: `[0.7000001810090166, 0.7000001810090166, 0.7000001810090166]`.

| family | mean teacher_lp | Δ lp | mean tok/s | Δ tok/s | mean wall_ms/prompt | Δ wall | mean est GFLOPs | Δ GFLOPs | n |
|--------|-----------------|------|------------|---------|---------------------|--------|-----------------|----------|---|
| H-LAYB | -12.5914 | — | 1697.9 | — | 12 | — | 6.111 | — | 3 |
| H-PRUNB | -11.1451 | +1.4463 | 2315.4 | +617.4 | 3 | -9 | 4.277 | -1.833 | 3 |

**Decision: KILL (lp change vs H-LAYB)**

Thin+prune util under LAYB — tip EARLY / util LAYB / PRUN unchanged.

Commands: `npm run nano:prunb` → `npm run nano:prunb:report`.
