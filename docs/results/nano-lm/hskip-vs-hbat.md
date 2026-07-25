# H-SKIP smoke — BAT→CHBAT skip CBAT (Pareto FLAG)

Honest throughput path: CHB chunk (B=256) under BAT without claiming CBAT as a parent. CBAT shown for context (Pareto FLAG). Kill if no wall/tok/s win vs BAT or GFLOPs > BAT·(1+δ).
Prompt pack: `n_prompts=4`; chunk=`256` target_tokens=`128`; mode `BAT→CHBAT skip CBAT vs BAT (+ CBAT context)`.

| family | mean teacher_lp | Δ lp vs BAT | mean tok/s | Δ tok/s | mean wall_ms | Δ wall | mean est GFLOPs | Δ GFLOPs | n |
|--------|-----------------|-------------|------------|---------|--------------|--------|-----------------|----------|---|
| H-BAT | -12.5933 | — | 1164.5 | — | 18 | — | 6.111 | — | 3 |
| H-CBAT | -12.5933 | — | 1769.1 | — | 4 | — | 9.734 | — | 3 |
| H-SKIP | -12.5933 | +0.0000 | 2600.9 | +1436.4 | 3 | -16 | 6.111 | +0.000 | 3 |

**Decision: PROMOTE (BAT→CHBAT skip CBAT; honest GFLOPs)**

On PROMOTE: card chain BAT→**CHBAT**/SKIP (CBAT demoted; code kept).

Commands: `npm run nano:skip` → `npm run nano:skip:report`.
