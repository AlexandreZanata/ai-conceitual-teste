# H-SUMCACHE smoke — hierarchical summary+tail PFB2

Decision: **PROMOTE (SUMCACHE k=2 unique≈2.00 elig≈0.50 switch≈0.25; code↑ story≥parent−ε; L_eff=522; active=352; wall=44≤full=43+5)**

Parent: `H-EARLY n=1 on summary+tail` · k=2 · temp=0.8 · mechanism: `GENC-scale hierarchical compress; BEAMKV; not CTX`

Context: L_eff=522 · active=352 · W=256 · S_c=64 · S_f=32 · wall_sum=44 ms · wall_full=43 ms

| arm | mean story_lp | mean code_lp | mean wall_ms | mean unique | mean n_elig | mean switch | n |
|-----|---------------|--------------|--------------|-------------|-------------|--------------|---|
| H-EARLY@SUM | -14.9927 | -15.4221 | 23 | 1.000 | 1.00 | 0.00 | 12 |
| H-SUMCACHE K=2 | -14.0297 | -12.4260 | 44 | 2.000 | 0.50 | 0.25 | 12 |

Tips unchanged. Wave Y H-SUMCACHE (hierarchy ≠ CTX full-KV).

Reproduce:
`npm run nano:sumcache` → `npm run nano:sumcache:report`

Next formal:
`npm run nano:formal:hsumcache` → `npm run nano:formal:hsumcache:report`
