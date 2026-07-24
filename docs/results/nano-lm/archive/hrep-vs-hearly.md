# H-REP smoke — rep-penalty / no-repeat under EARLY

Search `rep_penalty` + `no_repeat_ngram` with frozen H-EARLY exit knobs.
Kill if no quality win (lp ≤ EARLY) or worse wall vs EARLY.
Search λ=0.4 (latency-aware).

| family | mean teacher_lp | Δ lp | mean wall_ms | Δ wall | mean est GFLOPs | Δ GFLOPs | n |
|--------|-----------------|------|--------------|--------|-----------------|----------|---|
| H-EARLY | -16.2518 | — | 41 | — | 8.930 | — | 3 |
| H-REP | -16.2518 | +0.0000 | 42 | +1 | 8.930 | +0.000 | 3 |

**Decision: KILL (no quality win vs H-EARLY)**

Note: prior archive H-REP vs B4 KILL (wall↑). Wave J parent = EARLY tip.
Lesson: under tip EARLY, searched rep/ngram genes did not raise teacher_lp;
null-equivalent decode ties tip (wall slightly↑).

Commands: `npm run nano:rep` → `npm run nano:rep:report`.
