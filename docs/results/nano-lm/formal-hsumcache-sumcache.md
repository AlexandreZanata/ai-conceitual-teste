# Formal H-SUMCACHE — hierarchical summary+tail PFB2

Decision: **PROMOTE (SUMCACHE k=2 unique≈2.00 elig≈0.75 switch≈0.42; code↑ story≥parent−ε; L_eff=522; active=352; wall=44≤full=43+5)**

Parent: `H-EARLY n=1 on summary+tail (formal genes)` · k=2 · temp=0.8 · mechanism: `GENC-scale hierarchical compress; BEAMKV; not CTX`

Context: L_eff=522 · active=352 · W=256 · S_c=64 · S_f=32 · wall_sum=44 ms · wall_full=43 ms

| arm | mean story_lp | mean code_lp | mean wall_ms | mean unique | mean n_elig | mean switch | n |
|-----|---------------|--------------|--------------|-------------|-------------|--------------|---|
| H-EARLY@SUM | -10.2523 | -13.8621 | 25 | 1.000 | 1.00 | 0.00 | 12 |
| H-SUMCACHE K=2 | -9.0751 | -10.4223 | 44 | 2.000 | 0.75 | 0.42 | 12 |

Tips unchanged. Wave Y H-SUMCACHE (hierarchy ≠ CTX full-KV).

Reproduce:
`npm run nano:sumcache` → `npm run nano:sumcache:report`
