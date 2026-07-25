# H-ABS-PFB smoke — parent-fallback story-floor code BoN

Wave X absurd sandbox (CSAFE fix): EARLY K-beam decode → keep beams with `story_lp ≥ parent_story − ε` → commit `argmax code_teacher_lp` among eligible; if none eligible, commit **parent continuation** (≠ CSAFE max-story fallback; ≠ unconstrained CBON; ≠ INTERF α-mix). Parent = bare H-EARLY n=1 greedy on prog@128.

Frozen: K=4; PFB_TEMP=0.8; ε_lp=0.05; max_new=32; seeds=3; unique@K ≥1.5; mean_switch > 0.

**Decision: PROMOTE (ABS-PFB k=4 unique≈4.00 elig≈0.83 switch≈0.42; code↑ story≥parent−ε)**

## Arms

| arm | mean story_lp | mean code_lp | mean wall_ms | mean unique | mean n_elig | mean switch | n |
|-----|---------------|--------------|--------------|-------------|-------------|--------------|---|
| H-EARLY n=1 | -14.8854 | -16.2692 | 21 | 1.000 | 1.00 | 0.00 | 12 |
| H-ABS-PFB k=4 | -14.6921 | -12.8930 | 72 | 4.000 | 0.83 | 0.42 | 12 |

Code↑ Δ≈+3.38; story HOLD (slight↑); switch≈0.42 (5/12 rows); wall↑ ~3.4× (BoN cost).

Commands: `npm run nano:pfb` → `npm run nano:pfb:report`.
