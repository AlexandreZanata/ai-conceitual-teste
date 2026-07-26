# H-ROLL smoke — rolling W + summary; PFB2 per segment

Decision: **PROMOTE (ROLL k=2 unique≈2.00 elig≈0.62 switch≈0.40; code↑ story≥parent−ε; L_eff=394≫W=128; active=123≤W+S=160)**

Parent: `H-EARLY n=1 on rolled ctx` · k=2 · temp=0.8 · mechanism: `stride-summary cache + window W; BEAMKV; not CTX`

Context: L_eff=394 · W=128 · S=32 · mean_active=123 · n_segments=16

| arm | mean story_lp | mean code_lp | mean wall_ms | mean unique | mean n_elig | mean switch | n |
|-----|---------------|--------------|--------------|-------------|-------------|--------------|---|
| H-EARLY@ROLL | -15.7085 | -16.5709 | 12 | 1.000 | 1.00 | 0.00 | 48 |
| H-ROLL K=2 | -15.0397 | -13.1817 | 42 | 2.000 | 0.62 | 0.40 | 48 |

Tips unchanged. Wave Y H-ROLL (summary‖W ≠ CTX full-KV).

Reproduce:
`npm run nano:roll` → `npm run nano:roll:report`

Next formal:
`npm run nano:formal:hroll` → `npm run nano:formal:hroll:report`
