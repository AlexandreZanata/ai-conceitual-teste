# Formal H-BEAMKV — shared KV vs indep prefills

Decision: **PROMOTE (BEAMKV k=2 unique≈2.00 elig≈0.75 switch≈0.42; code↑ story≥parent−ε; wall↓ vs indep prefills)**

Parent: `H-QT int8 EARLY n=1 on B2 (formal genes; QPFB2 freeze)` · k=2 · bits=8 · temp=0.8 · mechanism: `prefill once + expand past; wall gate vs K indep KV prefills`

| arm | mean story_lp | mean code_lp | mean wall_ms | mean token_evals | mean unique | mean n_elig | mean switch | weight_bytes | n |
|-----|---------------|--------------|--------------|------------------|-------------|-------------|--------------|--------------|---|
| H-QT-int8 n=1 | -10.3233 | -14.1457 | 24 | — | 1.000 | 1.00 | 0.00 | 13629704 | 12 |
| H-BEAMKV-naive indep | -9.8093 | -10.9183 | 97 | 66.0 | 2.000 | 0.67 | 0.33 | 13629704 | 12 |
| H-BEAMKV shared | -9.7655 | -10.4274 | 51 | 65.0 | 2.000 | 0.75 | 0.42 | 13629704 | 12 |

Tips unchanged. Wave Y H-BEAMKV (cache on QPFB2 spine).

Reproduce:
`npm run nano:beamkv` → `npm run nano:beamkv:report`
