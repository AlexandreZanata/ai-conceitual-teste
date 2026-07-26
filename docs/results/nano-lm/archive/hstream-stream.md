# H-STREAM — PFB per chunk; parent=prev commit (**KILL**)

> Formal **KILL** (story collapse across T). Smoke had soft-ε PROMOTE but fit≠eval collapsed. Tooling purged.

Wave Y Y6: ingest rolled chunks (W=128, S=32, L≈384); seg0 parent=EARLY; later parent=previous PFB commit; gate = no story collapse + code non-decreasing (else HOLD).

## Smoke (matrix genes)

| arm | mean story_lp | mean code_lp | mean wall_ms | mean unique | mean switch | n |
|-----|---------------|--------------|--------------|-------------|-------------|---|
| parent (EARLY0/PREV) | -16.0358 | -14.4504 | 38 | 1.000 | 0.00 | 48 |
| H-STREAM K=2 | -15.4832 | -12.2354 | 43 | 2.000 | 0.50 | 48 |

story_series≈[-15.725, -14.688, -15.739, -15.782] · code_series≈[-13.262, -12.371, -11.729, -11.580]  
Smoke decision under COLLAPSE_EPS=0.5: **PROMOTE** (code non-decreasing; tiny story dip).

## Formal (fit≠eval)

| arm | mean story_lp | mean code_lp | mean wall_ms | mean unique | mean switch | n |
|-----|---------------|--------------|--------------|-------------|-------------|---|
| parent (EARLY0/PREV) | -10.9704 | -11.1601 | 38 | 1.000 | 0.00 | 48 |
| H-STREAM K=2 | -10.4036 | -9.4186 | 43 | 2.000 | 0.33 | 48 |

story_series≈[-9.737, -10.21, -10.872, -10.796] · code_series≈[-11.011, -9.728, -8.831, -8.104]

**Decision: KILL (story collapse across T=4)**

Code kept rising (Δ≈+2.9 from t0→t3) but story fell ≈1.1 LP vs t0 — fails “no story collapse”.

## Lesson

Chaining **parent=previous PFB commit** across rolled chunks can improve `code_teacher_lp` while **story drifts down** on later segments (different ctx + inherited continuation). Do not claim infinite stream. Prefer **H-ROLL** (independent EARLY parent per segment) or summary/KV session caches next (Y7+). Do not revive CTX/RAG.

Commands (purged): were `npm run nano:stream` / `nano:stream:report` / `nano:formal:hstream`.
