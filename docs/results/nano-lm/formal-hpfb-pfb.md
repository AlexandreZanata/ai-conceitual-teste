# Formal H-ABS-PFB — parent-fallback story-floor code BoN

Source: `results/nano-lm/formal-hpfb/formal.json`

Wave X absurd sandbox (CSAFE fix): EARLY K-beam decode → keep beams with `story_lp ≥ parent_story − ε` → commit `argmax code_teacher_lp` among eligible; if none eligible, commit **parent continuation**. Parent = bare H-EARLY n=1 (formal HEARLY genes / B2 ckpts) on prog@128. Dual gate: code↑ and story ≥ parent−ε; audit unique@K, n_elig, n_switch.

Frozen: K=4; PFB_TEMP=0.8; ε_lp=0.05; max_new=32; seeds=3.

## Teachers

| role | hf_id | params | license |
|------|-------|--------|---------|
| story | `roneneldan/TinyStories-33M` | 33M | TinyStories |
| code | `bigcode/tiny_starcoder_py` | 164000000 | BigCode OpenRAIL-M v1 |

**Decision: PROMOTE (ABS-PFB k=4 unique≈4.00 elig≈1.17 switch≈0.42; code↑ story≥parent−ε)**

## Arms

| arm | mean story_lp | mean code_lp | mean wall_ms | mean unique | mean n_elig | mean switch | n |
|-----|---------------|--------------|--------------|-------------|-------------|--------------|---|
| H-EARLY n=1 | -10.3233 | -14.1457 | 24 | 1.000 | 1.00 | 0.00 | 12 |
| H-ABS-PFB k=4 | -9.9450 | -10.3778 | 75 | 4.000 | 1.17 | 0.42 | 12 |

Code↑ Δ≈+3.77; story↑; switch≈0.42; wall↑ ~3.1×. Parent-fallback keeps dual gate when beams miss the story floor (CSAFE lesson confirmed).

Commands: `npm run nano:formal:hpfb` → `npm run nano:formal:hpfb:report`.
