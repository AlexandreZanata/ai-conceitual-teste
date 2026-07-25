# H-XFER2 smoke — PACK on elongated / OOD / OOD-long

PACK-only transfer deepen (Wave V). Kill if H-PACK loses dual gate vs EARLY on any pack. BPACK is report-only (does not fail the gate).
Mode: `transfer PACK (+BPACK report) on elongated/ood/ood_long`; packs=`{'elongated': {'n_prompts': 4, 'target_tokens': 256}, 'ood': {'n_prompts': 4, 'target_tokens': 128}, 'ood_long': {'n_prompts': 4, 'target_tokens': 256}}`.

| recipe | elongated | ood | ood_long |
|--------|-----------|-----|----------|
| H-PACK | PROMOTE (SERVE=min-wall + SROUTE=Pareto  | PROMOTE (SERVE=min-wall + SROUTE=Pareto  | KILL (SERVE lp change vs H-EARLY) |
| H-BPACK | KILL (SKIP GFLOPs↑ beyond tip+δ vs H-EAR | KILL (LAYB lp change vs H-EARLY) | KILL (SKIP GFLOPs↑ beyond tip+δ vs H-EAR |

**Decision: KILL (transfer fail H-PACK/ood_long: KILL (SERVE lp change vs H-EARLY))**

## Pack `elongated` (n=4, target=256)

### H-PACK

| family | mean teacher_lp | Δ lp | mean tok/s | Δ tok/s | mean wall_ms | Δ wall | mean est GFLOPs | n |
|--------|-----------------|------|------------|---------|--------------|--------|-----------------|---|
| H-EARLY | -12.1591 | — | 584.8 | — | 17 | — | 11.871 | 3 |
| H-SERVE | -12.1720 | -0.0129 | 1008.2 | +423.3 | 7 | -10 | 11.871 | 3 |
| H-SROUTE | -10.4305 | +1.7286 | 2134.6 | +1549.8 | 13 | -4 | 70.863 | 3 |

### H-BPACK (report-only)

| family | mean teacher_lp | Δ lp | mean tok/s | Δ tok/s | mean wall_ms | Δ wall | mean est GFLOPs | n |
|--------|-----------------|------|------------|---------|--------------|--------|-----------------|---|
| H-EARLY | -12.1591 | — | 653.3 | — | 10 | — | 11.871 | 3 |
| H-SKIP | -12.1591 | +0.0000 | 2480.8 | +1827.4 | 3 | -8 | 13.624 | 3 |
| H-LAYB | -12.1720 | -0.0129 | 2005.1 | +1351.8 | 4 | -7 | 12.747 | 3 |

## Pack `ood` (n=4, target=128)

### H-PACK

| family | mean teacher_lp | Δ lp | mean tok/s | Δ tok/s | mean wall_ms | Δ wall | mean est GFLOPs | n |
|--------|-----------------|------|------------|---------|--------------|--------|-----------------|---|
| H-EARLY | -10.3509 | — | 745.5 | — | 9 | — | 6.256 | 3 |
| H-SERVE | -10.3469 | +0.0040 | 1305.7 | +560.2 | 5 | -4 | 6.256 | 3 |
| H-SROUTE | -9.1707 | +1.1802 | 2292.2 | +1546.6 | 12 | +3 | 39.698 | 3 |

### H-BPACK (report-only)

| family | mean teacher_lp | Δ lp | mean tok/s | Δ tok/s | mean wall_ms | Δ wall | mean est GFLOPs | n |
|--------|-----------------|------|------------|---------|--------------|--------|-----------------|---|
| H-EARLY | -10.3509 | — | 767.6 | — | 9 | — | 6.256 | 3 |
| H-SKIP | -10.3509 | +0.0000 | 2751.7 | +1984.1 | 2 | -6 | 6.256 | 3 |
| H-LAYB | -10.4654 | -0.1145 | 2407.2 | +1639.6 | 3 | -6 | 6.256 | 3 |

## Pack `ood_long` (n=4, target=256)

### H-PACK

| family | mean teacher_lp | Δ lp | mean tok/s | Δ tok/s | mean wall_ms | Δ wall | mean est GFLOPs | n |
|--------|-----------------|------|------------|---------|--------------|--------|-----------------|---|
| H-EARLY | -10.3969 | — | 655.6 | — | 10 | — | 12.049 | 3 |
| H-SERVE | -10.4971 | -0.1002 | 1055.6 | +400.0 | 6 | -4 | 12.049 | 3 |
| H-SROUTE | -9.2368 | +1.1601 | 2141.8 | +1486.2 | 13 | +3 | 71.836 | 3 |

### H-BPACK (report-only)

| family | mean teacher_lp | Δ lp | mean tok/s | Δ tok/s | mean wall_ms | Δ wall | mean est GFLOPs | n |
|--------|-----------------|------|------------|---------|--------------|--------|-----------------|---|
| H-EARLY | -10.3969 | — | 657.6 | — | 10 | — | 12.049 | 3 |
| H-SKIP | -10.3969 | +0.0000 | 2514.1 | +1856.5 | 3 | -8 | 13.829 | 3 |
| H-LAYB | -10.4102 | -0.0133 | 1985.6 | +1327.9 | 4 | -6 | 12.939 | 3 |

Tips unchanged. Wave V PACK transfer deepen.

Commands: tooling purged after KILL (`nano:xfer2*` removed). Report retained for evidence.
