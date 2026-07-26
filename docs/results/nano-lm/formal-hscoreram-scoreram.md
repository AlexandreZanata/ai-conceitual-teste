# Formal H-SCORERAM — disk/RAM pack score cache

Decision: **PROMOTE (SCORERAM warm wall↓ hit_rate=1.00; lp unchanged)**

Parent: `PFB2 K=2 banks (formal genes; decode once)` · k=2 · temp=0.8 · mechanism: `PackScoreCache RAM+disk; TCACHE elig-only code on warm hit`

Score wall_ms: cold=3895 · warm=0

Forwards: cold=32 · warm=0 · hit_rate=1.00 · entries=32

| arm | mean story_lp | mean code_lp | mean unique | mean n_elig | mean switch | n |
|-----|---------------|--------------|-------------|-------------|--------------|---|
| cold (fill cache) | -9.6759 | -10.5426 | 2.000 | 0.67 | 0.42 | 12 |
| warm (disk hit) | -9.6759 | -10.5426 | 2.000 | 0.67 | 0.42 | 12 |

Tips unchanged. Wave Y H-SCORERAM (AMORT-like teacher pack cache).

Reproduce:
`npm run nano:scoreram` → `npm run nano:scoreram:report`
