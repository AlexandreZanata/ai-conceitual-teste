# Formal H-BPACK — SKIP + LAYB packs vs H-EARLY

Source: `results/nano-lm/formal-hbpack/formal.json`
Wall clock: 5.8s

Fit≠eval. Freeze SKIP + LAYB vs serial EARLY (|Δlp|≤ε + wall/tok/s↑; SKIP GFLOPs ≤ EARLY·(1+δ)).
n_prompts=10 chunk_size=`256` budgets=`[16, 64]` target_tokens=`128`.

| family | mean teacher_lp | Δ lp | mean tok/s | Δ tok/s | mean wall_ms | Δ wall | mean est GFLOPs | Δ GFLOPs | n |
|--------|-----------------|------|------------|---------|--------------|--------|-----------------|----------|---|
| H-EARLY | -13.9921 | — | 682.1 | — | 13 | — | 7.393 | — | 3 |
| H-SKIP | -13.9921 | +0.0000 | 4653.8 | +3971.7 | 2 | -11 | 7.393 | +0.000 | 3 |
| H-LAYB | -13.9918 | +0.0003 | 4555.1 | +3873.1 | 2 | -11 | 7.393 | +0.000 | 3 |

**Decision:** PROMOTE (SKIP+LAYB throughput packs vs EARLY)

Card hygiene (Wave T). Throughput packs frozen vs tip EARLY.

Commands: `npm run nano:formal:hbpack` → `npm run nano:formal:hbpack:report`.
