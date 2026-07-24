# H-WIN smoke — local sliding-window attention vs H-STAG

Train under STAG recipe (`seq_lo=6`, `n_stages=4`) with GPT-Neo local attn `window_size=32`.
FLOPs scale attention portion by min(1, window/seq). Kill if quality < STAG−ε or no FLOP win.

| family | mean teacher_lp | Δ lp | mean wall_ms | Δ wall | mean est GFLOPs | Δ GFLOPs | n |
|--------|-----------------|------|--------------|--------|-----------------|----------|---|
| H-STAG | -16.5349 | — | 48 | — | 6.751 | — | 3 |
| H-WIN | -16.6476 | -0.1128 | 40 | -8 | 6.213 | -0.539 | 3 |

**Decision: KILL (quality drop vs H-STAG)**

Commands: `npm run nano:win` → `npm run nano:win:report`.
