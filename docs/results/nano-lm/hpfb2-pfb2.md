# H-ABS-PFB2 smoke — PFB K=2 vs EARLY; wall↓ vs PFB k=4

Wave X efficiency follow-up to **H-ABS-PFB**: same story-floor + parent-fallback commit with **K=2** beams. Parent = H-EARLY n=1. Gate: dual quality vs EARLY **and** wall↓ vs same-run PFB k=4.

Frozen: K2=2; K4=4; PFB_TEMP=0.8; ε_lp=0.05; max_new=32; seeds=3.

**Decision: PROMOTE (ABS-PFB2 k=2 unique≈2.00 elig≈0.17 switch≈0.17; code↑ story≥parent−ε; wall↓ vs PFB k=4)**

## Arms

| arm | mean story_lp | mean code_lp | mean wall_ms | mean unique | mean n_elig | mean switch | n |
|-----|---------------|--------------|--------------|-------------|-------------|--------------|---|
| H-EARLY n=1 | -14.8854 | -16.2692 | 21 | 1.000 | 1.00 | 0.00 | 12 |
| H-ABS-PFB k=4 | -14.5517 | -12.2737 | 70 | 4.000 | 1.00 | 0.50 | 12 |
| H-ABS-PFB2 k=2 | -14.6424 | -14.2413 | 52 | 2.000 | 0.17 | 0.17 | 12 |

Code↑ Δ≈+2.03 vs EARLY; story HOLD; wall 52 vs PFB 70 (~26%↓). Switch lower than k=4 (fewer eligible hits).

Commands: `npm run nano:pfb2` → `npm run nano:pfb2:report`.
