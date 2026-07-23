# H-BLK smoke vs B3 (block-parallel decode)

Sample block_size tokens per forward (no mid-block AR reconditioning).
Kill if quality crash/drop vs B3 or no wall win.

| family | mean teacher_lp | mean wall_ms | Δ lp vs B3 | n |
|--------|-----------------|--------------|------------|---|
| B3 | -16.8704 | 39 | — | 3 |
| H-BLK | -16.9087 | 44 | -0.0383 | 3 |

**Decision: KILL (no speedup vs B3)**

Commands: `npm run nano:blk` → `npm run nano:blk:report`.
