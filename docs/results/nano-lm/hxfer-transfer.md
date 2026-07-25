# H-XFER smoke — PACK/QPACK/TPACK on heldout / elongated / OOD

Transfer audit: re-score official recipes on packs the harness did not claim on. Kill if any recipe loses its dual gate on any pack.
Mode: `transfer PACK/QPACK/TPACK on heldout/elongated/ood`; packs=`{'heldout': {'n_prompts': 2, 'target_tokens': 128}, 'elongated': {'n_prompts': 4, 'target_tokens': 256}, 'ood': {'n_prompts': 4, 'target_tokens': 128}}`.

| recipe | heldout | elongated | ood |
|--------|---------|-----------|-----|
| H-PACK | PROMOTE (SERVE=min-wall + SROUTE=Pareto  | PROMOTE (SERVE=min-wall + SROUTE=Pareto  | PROMOTE (SERVE=min-wall + SROUTE=Pareto  |
| H-QPACK | PROMOTE (FLAYB quality pack vs POOL) | PROMOTE (FLAYB quality pack vs POOL) | KILL (FLAYB quality drop vs H-POOL) |
| H-TPACK | KILL (quality drop vs H-STAG) | KILL (quality drop vs H-STAG) | KILL (quality drop vs H-STAG) |

**Decision: KILL (transfer fail H-QPACK/ood: KILL (FLAYB quality drop vs H-POOL))**

## Pack `heldout` (n=2, target=128)

### H-PACK

| family | mean teacher_lp | Δ lp | mean tok/s | Δ tok/s | mean wall_ms | Δ wall | mean est GFLOPs | n |
|--------|-----------------|------|------------|---------|--------------|--------|-----------------|---|
| H-EARLY | -11.3368 | — | 612.9 | — | 23 | — | 6.055 | 3 |
| H-SERVE | -11.3347 | +0.0020 | 1018.3 | +405.4 | 7 | -16 | 6.055 | 3 |
| H-SROUTE | -10.0581 | +1.2786 | 1422.9 | +809.9 | 21 | -1 | 38.618 | 3 |

### H-QPACK

| family | mean teacher_lp | Δ lp | mean tok/s | Δ tok/s | mean wall_ms | Δ wall | mean est GFLOPs | n |
|--------|-----------------|------|------------|---------|--------------|--------|-----------------|---|
| H-POOL | -9.5435 | — | 704.2 | — | 56 | — | 42.652 | 3 |
| H-FLAYB | -9.5424 | +0.0011 | 1542.3 | +838.1 | 24 | -32 | 43.092 | 3 |

### H-TPACK

| family | mean teacher_lp | Δ lp | mean ms/step | Δ ms/step | n |
|--------|-----------------|------|--------------|-----------|---|
| H-STAG | -18.0290 | — | 9.3 | — | 3 |
| H-TPACK | -18.6126 | -0.5836 | 6.2 | -3.1 | 3 |

## Pack `elongated` (n=4, target=256)

### H-PACK

| family | mean teacher_lp | Δ lp | mean tok/s | Δ tok/s | mean wall_ms | Δ wall | mean est GFLOPs | n |
|--------|-----------------|------|------------|---------|--------------|--------|-----------------|---|
| H-EARLY | -12.1591 | — | 632.7 | — | 10 | — | 11.871 | 3 |
| H-SERVE | -12.1720 | -0.0129 | 947.5 | +314.8 | 7 | -3 | 11.871 | 3 |
| H-SROUTE | -10.4305 | +1.7286 | 2084.3 | +1451.6 | 13 | +3 | 70.863 | 3 |

### H-QPACK

| family | mean teacher_lp | Δ lp | mean tok/s | Δ tok/s | mean wall_ms | Δ wall | mean est GFLOPs | n |
|--------|-----------------|------|------------|---------|--------------|--------|-----------------|---|
| H-POOL | -10.0343 | — | 634.5 | — | 62 | — | 77.548 | 3 |
| H-FLAYB | -10.0503 | -0.0160 | 2373.4 | +1738.9 | 16 | -47 | 79.408 | 3 |

### H-TPACK

| family | mean teacher_lp | Δ lp | mean ms/step | Δ ms/step | n |
|--------|-----------------|------|--------------|-----------|---|
| H-STAG | -18.2013 | — | 9.3 | — | 3 |
| H-TPACK | -18.4296 | -0.2283 | 6.2 | -3.1 | 3 |

## Pack `ood` (n=4, target=128)

### H-PACK

| family | mean teacher_lp | Δ lp | mean tok/s | Δ tok/s | mean wall_ms | Δ wall | mean est GFLOPs | n |
|--------|-----------------|------|------------|---------|--------------|--------|-----------------|---|
| H-EARLY | -10.3509 | — | 743.7 | — | 9 | — | 6.256 | 3 |
| H-SERVE | -10.3469 | +0.0040 | 1296.2 | +552.5 | 5 | -4 | 6.256 | 3 |
| H-SROUTE | -9.1707 | +1.1802 | 2254.5 | +1510.8 | 13 | +4 | 39.698 | 3 |

### H-QPACK

| family | mean teacher_lp | Δ lp | mean tok/s | Δ tok/s | mean wall_ms | Δ wall | mean est GFLOPs | n |
|--------|-----------------|------|------------|---------|--------------|--------|-----------------|---|
| H-POOL | -9.1405 | — | 710.6 | — | 56 | — | 43.858 | 3 |
| H-FLAYB | -9.2789 | -0.1384 | 2539.0 | +1828.4 | 15 | -41 | 44.313 | 3 |

### H-TPACK

| family | mean teacher_lp | Δ lp | mean ms/step | Δ ms/step | n |
|--------|-----------------|------|--------------|-----------|---|
| H-STAG | -16.5502 | — | 9.3 | — | 3 |
| H-TPACK | -16.7481 | -0.1979 | 6.2 | -3.1 | 3 |

Tips unchanged. Wave U transfer hygiene.

Commands: `npm run nano:xfer` → `npm run nano:xfer:report`.
