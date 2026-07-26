# Formal H-GPFB4-LONG — GPFB4∘ROLL

Source: `results/nano-lm/formal-hgpfb4long/formal.json`
Wall clock: 107.4s

Decision: **PROMOTE (GPFB4-LONG k=4 unique≈4.00 elig≈0.69 switch≈0.19; code↑ story≥parent−ε; L_eff=394≫W=128; active=123≤W+S=160; wall_roll≤full+slack)**

Parent: `H-GENC-serial n=1 on rolled ctx (formal HEARLY/B2)` · k=4 · temp=0.8 · gene0=`{'k_retrieve': 1, 'chunk_len': 32, 'stride': 32, 'quant_bits': 16, 'exit_depth': 1}` · mechanism: `compose GPFB4+ROLL; K=4 only; wall_roll≤full+slack`

Context: L_eff=394.25 · W=128 · S=32 · mean_active=122.5625 · n_segments=16

| arm | mean story_lp | mean code_lp | mean wall_ms | mean unique | mean n_elig | mean switch | n |
|-----|---------------|--------------|--------------|-------------|-------------|--------------|---|
| H-GENC-serial@ROLL | -9.5842 | -13.0772 | 11 | 1.000 | 1.00 | 0.00 | 48 |
| H-GPFB4-LONG k=4 | -9.3776 | -12.0232 | 56 | 4.000 | 0.69 | 0.19 | 48 |
| H-GPFB4-FULL@384 | -8.6965 | -15.5147 | 52 | 4.000 | 0.00 | 0.00 | 12 |

Tips unchanged. Wave Y GPFB4-LONG (compose; never K=2 / GENCACHE).

Reproduce:
`npm run nano:gpfb4long` → `npm run nano:gpfb4long:report`
