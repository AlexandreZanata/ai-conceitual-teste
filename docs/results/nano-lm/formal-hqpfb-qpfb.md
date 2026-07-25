# Formal H-ABS-QPFB — PFB on QT-int8 vs H-QT parent

Source: `results/nano-lm/formal-hqpfb/formal.json`

Wave X: **H-QT** int8 student + **H-ABS-PFB** commit vs H-QT EARLY n=1 (formal HEARLY genes / B2). Dual gate: code↑ and story ≥ parent−ε; audit unique@K, n_elig, n_switch, weight_bytes.

Frozen: K=4; PFB_TEMP=0.8; ε_lp=0.05; bits=8; max_new=32; seeds=3.

## Teachers

| role | hf_id | params | license |
|------|-------|--------|---------|
| story | `roneneldan/TinyStories-33M` | 33M | TinyStories |
| code | `bigcode/tiny_starcoder_py` | 164000000 | BigCode OpenRAIL-M v1 |

**Decision: PROMOTE (ABS-QPFB k=4 unique≈4.00 elig≈1.25 switch≈0.42; code↑ story≥parent−ε)**

## Arms

| arm | mean story_lp | mean code_lp | mean wall_ms | mean unique | mean n_elig | mean switch | weight_bytes | n |
|-----|---------------|--------------|--------------|-------------|-------------|--------------|--------------|---|
| H-QT-int8 n=1 | -10.3233 | -14.1457 | 25 | 1.000 | 1.00 | 0.00 | 13629704 | 12 |
| H-ABS-QPFB k=4 | -9.6123 | -10.5407 | 79 | 4.000 | 1.25 | 0.42 | 13629704 | 12 |

Code↑ Δ≈+3.61; story↑; switch≈0.42; wall↑ ~3.1×. PFB dual-gate **holds under int8** (QT∘PFB compose).

Commands: `npm run nano:formal:hqpfb` → `npm run nano:formal:hqpfb:report`.
