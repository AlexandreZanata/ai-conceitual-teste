# H-DEPTHA smoke — DEPTH student under ADAMF vs H-ADAMF

Same top-k soft cache, STAG curriculum, and ADAMF I/O (PRE+HALF+fused); only student depth differs (1-layer DEPTH vs tip). Kill if quality < ADAMF−ε or no ms/step win.
Recipe: `seq_lo=6`, `n_stages=4`, `steps=30`, `top_k=64`, mode `DEPTH student + ADAMF I/O vs full ADAMF`.

| family | mean teacher_lp | Δ lp | mean ms/step | Δ ms/step | mean train_wall_s | n |
|--------|-----------------|------|--------------|-----------|------------------|---|
| H-ADAMF | -16.6988 | — | 6.4 | — | 0.19 | 3 |
| H-DEPTHA | -16.7943 | -0.0956 | 5.0 | -1.4 | 0.15 | 3 |

**Decision: KILL (quality drop vs H-ADAMF)**

Tip H-ADAMF / H-DEPTH util unchanged unless PROMOTE. Thin+prune × train I/O.

Commands: `npm run nano:deptha` → `npm run nano:deptha:report`.
