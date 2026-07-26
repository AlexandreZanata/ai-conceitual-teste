# Formal H-ROLL — rolling W + summary; PFB2 per segment

Decision: **PROMOTE (ROLL k=2 unique≈2.00 elig≈0.73 switch≈0.38; code↑ story≥parent−ε; L_eff=394≫W=128; active=123≤W+S=160)**

Parent: `H-EARLY n=1 on rolled ctx (formal genes)` · k=2 · temp=0.8 · mechanism: `stride-summary cache + window W; BEAMKV; not CTX`

Context: L_eff=394 · W=128 · S=32 · mean_active=123 · n_segments=16

| arm | mean story_lp | mean code_lp | mean wall_ms | mean unique | mean n_elig | mean switch | n |
|-----|---------------|--------------|--------------|-------------|-------------|--------------|---|
| H-EARLY@ROLL | -10.9315 | -12.8011 | 13 | 1.000 | 1.00 | 0.00 | 48 |
| H-ROLL K=2 | -10.0072 | -9.4065 | 42 | 2.000 | 0.73 | 0.38 | 48 |

Tips unchanged. Wave Y H-ROLL (summary‖W ≠ CTX full-KV).

Reproduce:
`npm run nano:roll` → `npm run nano:roll:report`
