# H-GPFB4-LONG smoke — GPFB4∘ROLL

Decision: **PROMOTE (GPFB4-LONG k=4 unique≈4.00 elig≈0.71 switch≈0.31; code↑ story≥parent−ε; L_eff=394≫W=128; active=123≤W+S=160; wall_roll≤full+slack)**

Parent: `H-GENC-serial n=1 on rolled ctx` · k=4 · temp=0.8 · gene0=`{'k_retrieve': 1, 'chunk_len': 32, 'stride': 32, 'quant_bits': 16, 'exit_depth': 1}` · mechanism: `compose GPFB4+ROLL (Y4/Y5); never K=2; not GENCACHE/STREAM`

Context: L_eff=394.25 · W=128 · S=32 · mean_active=122.5625 · n_segments=16

| arm | mean story_lp | mean code_lp | mean wall_ms | mean unique | mean n_elig | mean switch | n |
|-----|---------------|--------------|--------------|-------------|-------------|--------------|---|
| H-GENC-serial@ROLL | -13.1291 | -15.5407 | 9 | 1.000 | 1.00 | 0.00 | 48 |
| H-GPFB4-LONG k=4 | -12.7761 | -13.2314 | 52 | 4.000 | 0.71 | 0.31 | 48 |
| H-GPFB4-FULL@384 | -12.4657 | -14.8068 | 52 | 4.000 | 0.67 | 0.25 | 12 |

Tips unchanged. Wave Y GPFB4-LONG (compose; never K=2 / GENCACHE).

Reproduce:
`npm run nano:gpfb4long` → `npm run nano:gpfb4long:report`

Next formal:
`npm run nano:formal:hgpfb4long` → `npm run nano:formal:hgpfb4long:report`
