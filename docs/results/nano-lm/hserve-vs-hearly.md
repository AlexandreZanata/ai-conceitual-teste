# H-SERVE smoke — full serving stack vs tip H-EARLY

Control: serial H-EARLY alone on long prompts / dual budgets. Candidate: best of speed=`CHB+LAY+GALL` or quality=`CHB+FLAYB+GRAPHF` (picked recipes: `speed`). Kill if |Δlp| > ε vs EARLY or no wall/tok/s win.
Prompt pack: `n_prompts=4`; budgets=`[16, 64]` chunk=`256` target_tokens=`128`; mode `best of GALL-speed / GRAPHF-quality vs serial EARLY`.

| family | mean teacher_lp | Δ lp | mean tok/s | Δ tok/s | mean wall_ms/prompt | Δ wall | mean est GFLOPs | Δ GFLOPs | n |
|--------|-----------------|------|------------|---------|---------------------|--------|-----------------|----------|---|
| H-EARLY | -12.5933 | — | 652.5 | — | 15 | — | 6.111 | — | 3 |
| H-SERVE | -12.5914 | +0.0019 | 1254.9 | +602.4 | 5 | -10 | 6.111 | +0.000 | 3 |

**Decision: PROMOTE (full serving stack vs EARLY)**

Tip H-EARLY unchanged unless PROMOTE. Full-stack serving claim.

Commands: `npm run nano:serve` → `npm run nano:serve:report`.
