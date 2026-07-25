# H-DEPTHB smoke — DEPTH_prun ckpt under LAYB decode

Same dual-budget LAYB path on frozen `HDEPTH_prun` (1-layer + prune) vs control H-LAYB on B2. GFLOPs density-scaled. Kill if |Δlp| > ε vs H-LAYB or no wall/GFLOPs win.
Prompt pack: smoke+fit elongated (`n_prompts=4`); budgets=`[16, 64]` target_tokens=`128`; mode `DEPTH_prun under LAYB vs B2+LAYB; dual-budget; long prompts`.
DEPTH densities per seed: `[0.7, 0.7, 0.7]`.

| family | mean teacher_lp | Δ lp | mean tok/s | Δ tok/s | mean wall_ms/prompt | Δ wall | mean est GFLOPs | Δ GFLOPs | n |
|--------|-----------------|------|------------|---------|---------------------|--------|-----------------|----------|---|
| H-LAYB | -12.5914 | — | 1775.7 | — | 10 | — | 6.111 | — | 3 |
| H-DEPTHB | -12.3921 | +0.1994 | 2950.3 | +1174.6 | 2 | -8 | 4.214 | -1.897 | 3 |

**Decision: KILL (lp change vs H-LAYB)**

Thin+prune util under LAYB — tip EARLY / util LAYB / DEPTH unchanged.

Commands: `npm run nano:depthb` → `npm run nano:depthb:report`.
