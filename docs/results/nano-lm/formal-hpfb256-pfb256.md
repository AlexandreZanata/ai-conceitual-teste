# Formal H-PFB256 — PFB2 on prog@256 vs EARLY@256

Decision: **PROMOTE (PFB256 k=2 unique≈2.00 elig≈0.42 switch≈0.25; code↑ story≥parent−ε; wall@256=47 vs @128=46)**

Parent: `H-EARLY n=1 @256 on B2 (formal genes)` · k=2 · temp=0.8 · mechanism: `elongate like DOM to L=256; BEAMKV shared KV; not CTX chunk`

Wall compare: PFB2@256=47 ms · PFB2@128=46 ms (L=256 vs 128)

| arm | mean story_lp | mean code_lp | mean wall_ms | mean unique | mean n_elig | mean switch | n |
|-----|---------------|--------------|--------------|-------------|-------------|--------------|---|
| H-EARLY@256 | -10.2551 | -14.3665 | 26 | 1.000 | 1.00 | 0.00 | 12 |
| H-PFB256 K=2 | -9.2219 | -11.7903 | 47 | 2.000 | 0.42 | 0.25 | 12 |

Tips unchanged. Wave Y H-PFB256 (elongate ≠ CTX chunked-KV).

Reproduce:
`npm run nano:pfb256` → `npm run nano:pfb256:report`
