# H-LAT2 smoke vs B4 (λ≥0.4 + n≤2 clamp)

Stronger latency penalty than H-LAT; gene `n` clamped to ≤2.
Kill if quality < B4−ε or no wall win vs B4.

| family | mean teacher_lp | mean wall_ms | Δ lp vs B4 | n |
|--------|-----------------|--------------|------------|---|
| B4 | -17.0202 | 55 | — | 3 |
| H-LAT | -16.7523 | 135 | +0.2679 | 3 |
| H-LAT2 | -16.3973 | 42 | +0.6229 | 3 |

**Decision: PROMOTE (quality@wall vs B4)**

Δ H-LAT2 vs B4 lp: +0.6229.

Commands: `npm run nano:lat2` → `npm run nano:lat2:report`.
