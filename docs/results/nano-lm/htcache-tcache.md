# H-TCACHE smoke — teacher LP memo on PFB2

Decision: **PROMOTE (TCACHE k=2 unique≈2.00 elig≈0.42 switch≈0.25; code↑ story≥parent−ε; forwards↓≥30%; wall≤naive)**

Parent: `H-EARLY n=1 greedy on B2 (PFB2 recipe freeze)` · k=2 · temp=0.8 · mechanism: `TeacherLpMemo by completion id; code forwards only if story-eligible`

Score forwards: naive=48 · tcache=29 · drop=39.6% · hit_rate=0.00

Score wall_ms: naive=7886 · tcache=3406

| arm | mean story_lp | mean code_lp | mean wall_ms | mean unique | mean n_elig | mean switch | n |
|-----|---------------|--------------|--------------|-------------|-------------|--------------|---|
| H-EARLY n=1 | -14.8854 | -16.2692 | 21 | 1.000 | 1.00 | 0.00 | 12 |
| H-TCACHE-naive | -14.7000 | -14.6412 | 58 | 2.000 | 0.42 | 0.25 | 12 |
| H-TCACHE | -14.7000 | -14.6412 | 58 | 2.000 | 0.42 | 0.25 | 12 |

Tips unchanged. Wave Y H-TCACHE (teacher memo on PFB2 spine).

Reproduce:
`npm run nano:tcache` → `npm run nano:tcache:report`

Next formal:
`npm run nano:formal:htcache` → `npm run nano:formal:htcache:report`
