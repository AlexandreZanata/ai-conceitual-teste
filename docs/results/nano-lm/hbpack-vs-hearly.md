# H-BPACK smoke — SKIP + LAYB throughput packs vs H-EARLY

Card hygiene (batch axis): freeze SKIP (honest CHB chunk) and LAYB (throughput tip) against serial EARLY. Both need |Δlp|≤ε and wall/tok/s↑; SKIP must not inflate GFLOPs beyond EARLY·(1+δ).
Prompt pack: `n_prompts=4`; budgets=`[16, 64]` chunk=`256` target_tokens=`128`; mode `SKIP+LAYB throughput packs vs EARLY`.

| family | mean teacher_lp | Δ lp | mean tok/s | Δ tok/s | mean wall_ms | Δ wall | mean est GFLOPs | Δ GFLOPs | n |
|--------|-----------------|------|------------|---------|--------------|--------|-----------------|----------|---|
| H-EARLY | -12.5933 | — | 644.2 | — | 16 | — | 6.111 | — | 3 |
| H-SKIP | -12.5933 | +0.0000 | 2119.8 | +1475.6 | 4 | -12 | 6.111 | +0.000 | 3 |
| H-LAYB | -12.5914 | +0.0019 | 2262.7 | +1618.4 | 3 | -12 | 6.111 | +0.000 | 3 |

**Decision: PROMOTE (SKIP+LAYB throughput packs vs EARLY)**

Tip H-EARLY unchanged. Throughput packs: SKIP mid, LAYB tip.

Commands: `npm run nano:bpack` → `npm run nano:bpack:report`.
