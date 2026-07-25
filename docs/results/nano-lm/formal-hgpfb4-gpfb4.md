# Formal H-ABS-GPFB4 — GENC∘PFB K=4

Source: `results/nano-lm/formal-hgpfb4/formal.json`

Wave X: **H-ABS-GPFB** K=2 KILL lesson → separate **K=4** claim under frozen H-GENC smoke genomes. Parent = GENC-serial n=1 (same gene). Dual gate: code↑ and story ≥ parent−ε; diversity/switch required (no wall↓ vs k=2).

Frozen: K=4; PFB_TEMP=0.8; ε_lp=0.05; max_new=32; seeds=3; gene0=`{k_retrieve:1, chunk_len:32, stride:32, quant_bits:16, exit_depth:1}`.

## Teachers

| role | hf_id | params | license |
|------|-------|--------|---------|
| story | `roneneldan/TinyStories-33M` | 33M | TinyStories |
| code | `bigcode/tiny_starcoder_py` | 164000000 | BigCode OpenRAIL-M v1 |

**Decision: PROMOTE (ABS-GPFB4 k=4 unique≈4.00 elig≈1.33 switch≈0.33; code↑ story≥parent−ε)**

## Arms

| arm | mean story_lp | mean code_lp | mean wall_ms | mean unique | mean n_elig | mean switch | n |
|-----|---------------|--------------|--------------|-------------|-------------|--------------|---|
| H-GENC-serial n=1 | -8.9141 | -13.9039 | 18 | 1.000 | 1.00 | 0.00 | 12 |
| H-ABS-GPFB4 k=4 | -8.7336 | -11.2748 | 52 | 4.000 | 1.33 | 0.33 | 12 |

Code↑ Δ≈+2.63 vs GENC-serial; story↑; unique@K≈4.00. GENC∘PFB K=4 dual-gates where GPFB K=2 did not.

Commands: `npm run nano:formal:hgpfb4` → `npm run nano:formal:hgpfb4:report`.
