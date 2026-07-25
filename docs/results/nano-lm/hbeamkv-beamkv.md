# H-BEAMKV smoke — shared KV vs indep prefills on QT PFB K=2

Decision: **PROMOTE (BEAMKV k=2 unique≈2.00 elig≈0.42 switch≈0.25; code↑ story≥parent−ε; wall↓ vs indep prefills)**

Parent: `H-QT int8 EARLY n=1 on B2 (QPFB2 recipe freeze)` · k=2 · bits=8 · temp=0.8 · mechanism: `prefill once + expand past; wall gate vs K indep KV prefills`

| arm | mean story_lp | mean code_lp | mean wall_ms | mean token_evals | mean unique | mean n_elig | mean switch | weight_bytes | n |
|-----|---------------|--------------|--------------|------------------|-------------|-------------|--------------|--------------|---|
| H-QT-int8 n=1 | -14.8854 | -16.2692 | 22 | — | 1.000 | 1.00 | 0.00 | 13629704 | 12 |
| H-BEAMKV-naive indep | -14.6349 | -13.9006 | 92 | 66.0 | 2.000 | 0.42 | 0.33 | 13629704 | 12 |
| H-BEAMKV shared | -14.6016 | -14.7786 | 50 | 65.0 | 2.000 | 0.42 | 0.25 | 13629704 | 12 |

Tips unchanged. Wave Y H-BEAMKV (cache on QPFB2 spine).

Reproduce:
`npm run nano:beamkv` → `npm run nano:beamkv:report`

Next formal:
`npm run nano:formal:hbeamkv` → `npm run nano:formal:hbeamkv:report`
