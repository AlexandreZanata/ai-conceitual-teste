# Formal H-TCACHE — teacher LP memo on PFB2

Decision: **PROMOTE (TCACHE k=2 unique≈2.00 elig≈0.75 switch≈0.42; code↑ story≥parent−ε; forwards↓≥30%; wall≤naive)**

Parent: `H-EARLY n=1 greedy on B2 (formal genes; PFB2 freeze)` · k=2 · temp=0.8 · mechanism: `TeacherLpMemo by completion id; code forwards only if story-eligible`

Score forwards: naive=48 · tcache=33 · drop=31.2% · hit_rate=0.00

Score wall_ms: naive=6509 · tcache=3854

| arm | mean story_lp | mean code_lp | mean wall_ms | mean unique | mean n_elig | mean switch | n |
|-----|---------------|--------------|--------------|-------------|-------------|--------------|---|
| H-EARLY n=1 | -10.3233 | -14.1457 | 23 | 1.000 | 1.00 | 0.00 | 12 |
| H-TCACHE-naive | -9.6957 | -10.3613 | 53 | 2.000 | 0.75 | 0.42 | 12 |
| H-TCACHE | -9.6957 | -10.3613 | 53 | 2.000 | 0.75 | 0.42 | 12 |

Tips unchanged. Wave Y H-TCACHE (teacher memo on PFB2 spine).

Reproduce:
`npm run nano:tcache` → `npm run nano:tcache:report`
