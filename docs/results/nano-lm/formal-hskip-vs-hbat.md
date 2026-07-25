# Formal H-SKIP vs H-BAT (skip CBAT Pareto FLAG)

Source: `results/nano-lm/formal-hskip/formal.json`
Wall clock: 3.0s

Fit≠eval. CHB chunk under BAT vs flat BAT. Kill if no wall/tok/s win or GFLOPs > BAT·(1+δ). CBAT is context only.
n_prompts=8 chunk_size=`256` target_tokens=`128`.

| family | mean teacher_lp | Δ lp vs BAT | mean tok/s | Δ tok/s | mean wall_ms | Δ wall | mean est GFLOPs | Δ GFLOPs | n |
|--------|-----------------|-------------|------------|---------|--------------|--------|-----------------|----------|---|
| H-BAT | -13.9854 | — | 1764.4 | — | 10 | — | 7.410 | — | 3 |
| H-CBAT | -13.9854 | — | 3327.7 | — | 2 | — | 11.057 | — | 3 |
| H-SKIP | -13.9854 | +0.0000 | 4559.5 | +2795.1 | 2 | -9 | 7.410 | +0.000 | 3 |

**Decision:** PROMOTE (BAT→CHBAT skip CBAT; honest GFLOPs)

Throughput hygiene (Wave S). Tip EARLY unchanged.

Commands: `npm run nano:formal:hskip` → `npm run nano:formal:hskip:report`.
