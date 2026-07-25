# Formal H-ABS-QPFB2 — PFB K=2 on QT; wall↓ vs QPFB k=4

Decision: **PROMOTE (ABS-QPFB2 k=2 unique≈2.00 elig≈0.58 switch≈0.33; code↑ story≥parent−ε; wall↓ vs QPFB k=4)**

Parent: `H-QT int8 EARLY n=1 on B2 (formal genes)` · k2=2 · k4=4 · bits=8 · temp=0.8 · mechanism: `quantize_student_int8 then PFB K=2; wall gate vs QPFB k=4`

| arm | mean story_lp | mean code_lp | mean wall_ms | mean unique | mean n_elig | mean switch | weight_bytes | n |
|-----|---------------|--------------|--------------|-------------|-------------|--------------|--------------|---|
| H-QT-int8 n=1 | -10.3233 | -14.1457 | 25 | 1.000 | 1.00 | 0.00 | 13629704 | 12 |
| H-ABS-QPFB k=4 | -9.7349 | -10.4135 | 79 | 4.000 | 1.42 | 0.42 | 13629704 | 12 |
| H-ABS-QPFB2 k=2 | -9.8159 | -11.1390 | 65 | 2.000 | 0.58 | 0.33 | 13629704 | 12 |

Tips unchanged. Wave X ABS-QPFB2 (QT∘PFB2).

Reproduce:
`npm run nano:qpfb2` → `npm run nano:qpfb2:report`

Next formal:
`npm run nano:formal:hqpfb2` → `npm run nano:formal:hqpfb2:report`
