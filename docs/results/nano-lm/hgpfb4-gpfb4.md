# H-ABS-GPFB4 smoke — GENC∘PFB K=4

Decision: **PROMOTE (ABS-GPFB4 k=4 unique≈4.00 elig≈0.67 switch≈0.33; code↑ story≥parent−ε)**

Parent: `H-GENC-serial n=1 (same genome, no beam)` · k=4 · temp=0.8 · gene0=`{'k_retrieve': 1, 'chunk_len': 32, 'stride': 32, 'quant_bits': 16, 'exit_depth': 1}` · mechanism: `frozen GENC gene; serial decode on GENC ctx; PFB K=4 (GPFB K=2 KILL lesson)`

| arm | mean story_lp | mean code_lp | mean wall_ms | mean unique | mean n_elig | mean switch | n |
|-----|---------------|--------------|--------------|-------------|-------------|--------------|---|
| H-GENC-serial n=1 | -12.9634 | -15.8878 | 19 | 1.000 | 1.00 | 0.00 | 12 |
| H-ABS-GPFB4 k=4 | -12.8475 | -13.8604 | 52 | 4.000 | 0.67 | 0.33 | 12 |

Tips unchanged. Wave X ABS-GPFB4 (GPFB K=2 KILL → separate k=4 ID).

Reproduce:
`npm run nano:gpfb4` → `npm run nano:gpfb4:report`

Next formal:
`npm run nano:formal:hgpfb4` → `npm run nano:formal:hgpfb4:report`
