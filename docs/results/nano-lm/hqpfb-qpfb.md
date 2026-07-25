# H-ABS-QPFB smoke — PFB on QT-int8 vs H-QT parent

Wave X: compose **H-QT** int8 student with **H-ABS-PFB** commit (story-floor → max code; empty-elig → parent). Parent = H-QT EARLY n=1 (not fp EARLY). Tests whether PFB dual-gate survives weight-only quantization.

Frozen: K=4; PFB_TEMP=0.8; ε_lp=0.05; bits=8; max_new=32; seeds=3.

**Decision: PROMOTE (ABS-QPFB k=4 unique≈4.00 elig≈0.75 switch≈0.50; code↑ story≥parent−ε)**

## Arms

| arm | mean story_lp | mean code_lp | mean wall_ms | mean unique | mean n_elig | mean switch | weight_bytes | n |
|-----|---------------|--------------|--------------|-------------|-------------|--------------|--------------|---|
| H-QT-int8 n=1 | -14.8854 | -16.2692 | 23 | 1.000 | 1.00 | 0.00 | 13629704 | 12 |
| H-ABS-QPFB k=4 | -14.5449 | -12.4442 | 79 | 4.000 | 0.75 | 0.50 | 13629704 | 12 |

Code↑ Δ≈+3.83; story↑; switch≈0.50; wall↑ ~3.4× (BoN cost; mem same as QT).

Commands: `npm run nano:qpfb` → `npm run nano:qpfb:report`.
