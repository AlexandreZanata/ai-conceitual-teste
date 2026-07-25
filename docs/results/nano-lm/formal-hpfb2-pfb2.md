# Formal H-ABS-PFB2 — PFB K=2 vs EARLY; wall↓ vs PFB k=4

Source: `results/nano-lm/formal-hpfb2/formal.json`

Wave X: **H-ABS-PFB** commit with **K=2** vs H-EARLY n=1 (formal HEARLY/B2). Same-run PFB k=4 is the efficiency parent for wall. Dual gate: code↑ and story ≥ EARLY−ε; plus wall↓ vs PFB k=4.

Frozen: K2=2; K4=4; PFB_TEMP=0.8; ε_lp=0.05; max_new=32; seeds=3.

## Teachers

| role | hf_id | params | license |
|------|-------|--------|---------|
| story | `roneneldan/TinyStories-33M` | 33M | TinyStories |
| code | `bigcode/tiny_starcoder_py` | 164000000 | BigCode OpenRAIL-M v1 |

**Decision: PROMOTE (ABS-PFB2 k=2 unique≈2.00 elig≈0.67 switch≈0.33; code↑ story≥parent−ε; wall↓ vs PFB k=4)**

## Arms

| arm | mean story_lp | mean code_lp | mean wall_ms | mean unique | mean n_elig | mean switch | n |
|-----|---------------|--------------|--------------|-------------|-------------|--------------|---|
| H-EARLY n=1 | -10.3233 | -14.1457 | 23 | 1.000 | 1.00 | 0.00 | 12 |
| H-ABS-PFB k=4 | -9.7106 | -10.5656 | 72 | 4.000 | 1.33 | 0.42 | 12 |
| H-ABS-PFB2 k=2 | -9.6443 | -11.2096 | 52 | 2.000 | 0.67 | 0.33 | 12 |

Code↑ Δ≈+2.94 vs EARLY; story↑; wall 52 vs PFB 72 (~28%↓). K=2 is the cheaper PFB default when wall matters.

Commands: `npm run nano:formal:hpfb2` → `npm run nano:formal:hpfb2:report`.
