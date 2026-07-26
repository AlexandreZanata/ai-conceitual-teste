# H-GENCACHE — evolve {W,S,k,ttl} under BUD vs QPFB2 (**KILL**)

> Smoke **KILL**. Mem↓ and slight wall↓, but story (and code) fell below QPFB2−ε. Tooling purged.

Wave Y Y9: GENC-style GA over ROLL/TTL phenotype `{W, summary_bits→S, k_beam=2, cache_ttl}` on prog@384; parent = QT∘PFB2 on full claim texts; gate = floors + BUD wall + Pareto on code↑×wall↓×mem↓.

## Smoke

| arm | mean story_lp | mean code_lp | mean wall_ms | mean_mem | n |
|-----|---------------|--------------|--------------|----------|---|
| QPFB2 parent | -14.2374 | -10.0639 | 54 | 391 | 6 |
| H-GENCACHE best | -14.7412 | -13.5702 | 48 | 169 | 22 |

Best genes (seeds 0/1/2): `{W:64,S:32,ttl:1}` · `{W:256,S:32,ttl:1}` · `{W:256,S:32,ttl:2}` · k_beam=2 fixed.

**Decision: KILL (story_lp -14.7412 < C0−ε -14.2874)**

Active mem ≈O(W+S) as intended (391→169) and wall edged down (54→48), but rolling+TTL phenotype lost story floor vs full-context QPFB2; code also collapsed (−10.06→−13.57). Not a 3-axis Pareto win.

## Lesson

Do not evolve ROLL budgets against a full-prefill QPFB2 parent expecting story parity — compression that wins mem/wall still fails the dual-quality floor. Keep **fixed** PROMOTE stacks: ROLL / SUMCACHE / QPFB2 as frozen recipes; do not GA-compose them into GENCACHE. Not GENQ. Next: **H-GPFB4-LONG** (compose only; no new cache genetics).

Commands (purged): were `npm run nano:gencache` / `nano:gencache:report` / `nano:formal:hgencache`.
