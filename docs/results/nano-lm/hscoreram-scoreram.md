# H-SCORERAM smoke — disk/RAM pack score cache

Decision: **PROMOTE (SCORERAM warm wall↓ hit_rate=1.00; lp unchanged)**

Parent: `PFB2 K=2 banks (decode once; score cold vs warm)` · k=2 · temp=0.8 · mechanism: `PackScoreCache RAM+disk; TCACHE elig-only code on warm hit`

Score wall_ms: cold=4352 · warm=0

Forwards: cold=32 · warm=0 · hit_rate=1.00 · entries=32

| arm | mean story_lp | mean code_lp | mean unique | mean n_elig | mean switch | n |
|-----|---------------|--------------|-------------|-------------|--------------|---|
| cold (fill cache) | -14.6236 | -12.5932 | 2.000 | 0.67 | 0.50 | 12 |
| warm (disk hit) | -14.6236 | -12.5932 | 2.000 | 0.67 | 0.50 | 12 |

Tips unchanged. Wave Y H-SCORERAM (AMORT-like teacher pack cache).

Reproduce:
`npm run nano:scoreram` → `npm run nano:scoreram:report`

Next formal:
`npm run nano:formal:hscoreram` → `npm run nano:formal:hscoreram:report`
