# H-PFB256 smoke — PFB2 on prog@256 vs EARLY@256

Decision: **PROMOTE (PFB256 k=2 unique≈2.00 elig≈0.58 switch≈0.33; code↑ story≥parent−ε; wall@256=46 vs @128=44)**

Parent: `H-EARLY n=1 @256 on B2` · k=2 · temp=0.8 · mechanism: `elongate like DOM to L=256; BEAMKV shared KV; not CTX chunk`

Wall compare: PFB2@256=46 ms · PFB2@128=44 ms (L=256 vs 128)

| arm | mean story_lp | mean code_lp | mean wall_ms | mean unique | mean n_elig | mean switch | n |
|-----|---------------|--------------|--------------|-------------|-------------|--------------|---|
| H-EARLY@256 | -15.3158 | -17.7361 | 24 | 1.000 | 1.00 | 0.00 | 12 |
| H-PFB256 K=2 | -14.0330 | -13.2348 | 46 | 2.000 | 0.58 | 0.33 | 12 |

Tips unchanged. Wave Y H-PFB256 (elongate ≠ CTX chunked-KV).

Reproduce:
`npm run nano:pfb256` → `npm run nano:pfb256:report`

Next formal:
`npm run nano:formal:hpfb256` → `npm run nano:formal:hpfb256:report`
